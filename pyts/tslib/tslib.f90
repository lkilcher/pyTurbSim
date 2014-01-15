MODULE tslib
!use, intrinsic :: iso_c_binding

CONTAINS

FUNCTION INDX(ii,jj,np)
  ! Returns the 'lower triangular' index for an array np x np array.
  !
  ! indx is equivalent to:
  ! indx=0
  ! DO jj=1,np
  !   DO ii=jj,np
  !     indx+indx+1
  !   ENDDO
  ! ENDDO
  indx=(jj-1)*np+ii-(jj*(jj-1))/2
  RETURN
END FUNCTION INDX

subroutine veers84(spec, Sij, phr, ncore, np, nf)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "VEERS84" :: VEERS84
!DEC$ ATTRIBUTES REFERENCE :: SPEC,SIJ,PHR,NP,NF
  ! This function performs the math in Veers1984 equations 7 and 8.
  ! The full reference is:
  !     Veers, Paul (1984) 'Modeling Stochastic Wind Loads on Vertical Axis Wind Turbines',
  !          Sandia Report 1909, 17 pages.
  !
  ! Inputs:
  ! Sij    - The packed-form (np*(np+1)/2,nf) full cross-spectral matrix.
  ! phr    - The random phases for each point for each frequency (np,nf).
  ! np,nf  - The number of points and number of frequencies.
  !
  ! Returns:
  !  The inverse FFT of the timeseries at each point (np,nf+1). Simply take the inverse 
  !  fft of this array to obtain the timeseries.
  !
  implicit none
  !f2py depend() np,nf
  !f2py integer np=shape(phr,0)
  !f2py integer nf=shape(phr,1)
  integer, intent(in)         :: np, nf, ncore
  real,intent(in)             :: Sij(np*(np+1)/2,nf)  ! This is the lower-triangular piece
                                                      ! of a (np,np,nf) shaped matrix.
  complex,intent(in)          :: phr(np,nf)        
  !real,intent(in)     :: Sii(np,nf)
  complex,intent(inout)         :: spec(np,nf)
  integer :: ii,jj!,indx
  integer :: ff,stat

  IF (ncore > 0) THEN
     CALL OMP_SET_NUM_THREADS(ncore)
  ENDIF

  ! This does a Cholesky factorization for each frequency.
  ! A Cholesky factorization *is* Veers84's equation 7, it converts the cross-spectral
  ! matrix Sij to Veers' H matrix.
  !$omp parallel private(stat , ff ) shared( Sij , np)
  !$omp do schedule( dynamic )
  DO ff=1,nf
     CALL SPPTRF('L',np,Sij(:,ff),stat) ! Cholesky Factorization
     !$print *, stat
  ENDDO
  !$omp end do
  !$omp end parallel

  !indx=0 ! Index for the lower-triangular matrix Sij (i.e. Veers84 'H').
  !$omp parallel private(ii, jj) default(shared)
  !$omp do schedule( dynamic )
  DO ii=1,np
     ! omp'single' directive unnecessary b/c parallel only applies to the outer loop.
     DO jj=1,ii
        !Note: we must compute the index (as below) rather than 
        !indx=(jj-1)*(np+1)+ii-jj+1-(jj*(jj-1))/2
        ! The first column needs to be zeros (for numpy.irfft; zero at the zero frequency); i.e. the '2:'.
        spec(ii,:)=spec(ii,:)+Sij(indx(ii,jj,np),:)*phr(jj,:) ! Multiply the columns of the H matrix (Sij) by the random phases (phr) and sum the rows.
     ENDDO
  ENDDO
  !$omp end do
  !$omp end parallel
  ! Note that we can sum the spectra (rather than the timeseries' as in Veers84) because 
  ! the Fourier Transform is a linear operation.  This reduces the number of inverse FFTs computed by n_p-1.
  RETURN
end subroutine veers84


subroutine ieccoh(Sij,f,y,z,uhub,a,Lc,ncore,nf,ny,nz)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "IECCOH" :: IECCOH
!DEC$ ATTRIBUTES REFERENCE :: SIJ,F,Y,Z,UHUB,A,LC,NCORE,NF,NY,NZ
  use omp_lib
  implicit none
  real,intent(inout)      :: Sij(ny*nz*(ny*nz+1)/2,nf)
  real,intent(in)       :: f(nf),y(ny),z(nz),uhub,a,Lc
  integer, intent(in)   :: nf,ny,nz,ncore
  integer       :: ind,ii,jj,iz(ny*nz),iy(ny*nz)
  real          :: r, ftmp(nf)

  IF (ncore > 0) THEN
     CALL OMP_SET_NUM_THREADS(ncore)
  ENDIF

  DO ii=1,ny*nz ! The arrays are in fortran order.
     iz(ii)=mod(ii-1,ny)+1
     iy(ii)=(ii-1)/ny+1
  ENDDO

  ind=0
  ftmp=SQRT((f/uhub)**2+(0.12/Lc)**2)
  !$omp parallel private(ii , jj, r, ind ) default(shared)
  !$omp do schedule( dynamic )
  DO jj=1,ny*nz
     DO ii=jj,ny*nz
        ind=indx(ii,jj,ny*nz)
        !ind=ind+1
        if (ii==jj) THEN
           Sij(ind,:)=1
        ELSE
           r=SQRT( (y( iy(ii) )-y( iy(jj) ))**2+( z(iz(ii)) - z( iz(jj) ))**2 )
           Sij(ind,:)=EXP(-1*a*r*ftmp)
        ENDIF
     ENDDO
  ENDDO
  !$omp end do
  !$omp end parallel

  RETURN

end subroutine ieccoh

subroutine nonIECcoh(Sij,f,y,z,u,coef_a,coef_b,coefExp,ncore,nf,ny,nz)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "NONIECCOH" :: NONIECCOH
!DEC$ ATTRIBUTES REFERENCE :: SIJ,F,Y,Z,U,COEFS,COEFEXP,NCORE,NF,NY,NZ
  use omp_lib
  implicit none
  real,intent(inout)    :: Sij(ny*nz*(ny*nz+1)/2,nf)
  real,intent(in)     :: coef_a,coef_b,coefExp
  real,intent(in)     :: y(ny), z(nz), u(ny*nz), f(nf)
  integer, intent(in) :: nf, ny, nz, ncore
  integer             :: ii, jj, ind, np!, ind2
  integer             :: iy(ny*nz), iz(ny*nz)
  real                :: r, tmp(nf), f2(nf), tmp_a, tmp_b
  np=ny*nz

  IF (ncore > 0) THEN
     CALL OMP_SET_NUM_THREADS(ncore)
  ENDIF

  DO ii=1,np ! The arrays are in fortran order.
     iz(ii)=mod(ii-1,ny)+1
     iy(ii)=(ii-1)/ny+1
  ENDDO
  
  !print *, coef_a,coef_b,coefexp,u,z,y

  tmp_b=coef_b**2
  IF (tmp_b/=0) THEN ! Square the frequency
     f2=f**2
  ENDIF
  !print *, 'start coh'
  !$omp parallel private(ii , jj, r, tmp, ind, tmp_a ) default(shared)
  !$omp do schedule( dynamic )
  DO jj=1,np ! The packmat (Sij) needs to be in column order for lapack's SPPTRF.
     DO ii=jj,np
        !ind=ind+1
        ind=indx(ii,jj,np)
        !print *, ind,ind2,jj,(jj*(jj-1))/2
        if ( ii == jj ) THEN
           Sij(ind,:)=1
        ELSE
           r=SQRT ( (y( iy(ii) )-y( iy(jj) ))**2+( z(iz(ii)) - z( iz(jj) ))**2 )
           if ( coefExp/=0 ) THEN
              tmp_a=-1*coef_a*(2.*r/(z(iz(ii))+z(iz(jj))))**coefExp
           ELSE
              tmp_a=-1*coef_a
           ENDIF
           IF (tmp_b==0) THEN
              tmp=r*f/((u(ii)+u(jj))/2.) ! r*f/u_mean
           ELSE
              tmp=r*SQRT(f2/((u(ii)+u(jj))/2.)**2+tmp_b) ! r*SQRT(f**2/u_mean**2+coef_b**2)
           ENDIF
           Sij(ind,:)=EXP(tmp_a*tmp)
        ENDIF
     ENDDO
  ENDDO
  !$omp end do
  !$omp end parallel
  !print *, 'end coh'

  RETURN
end subroutine nonIECcoh


END MODULE tslib
