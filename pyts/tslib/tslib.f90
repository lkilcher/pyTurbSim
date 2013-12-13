!use, intrinsic :: iso_c_binding

subroutine veers84(Sij, phr, np, nf,spec)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "VEERS84" :: VEERS84
!DEC$ ATTRIBUTES REFERENCE :: SIJ,PHR,NP,NF,SPEC
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
  integer, intent(in)         :: np, nf
  real,intent(in)             :: Sij(np*(np+1)/2,nf)  ! This is the lower-triangular piece
                                                      ! of a (np,np,nf) shaped matrix.
  complex,intent(in)          :: phr(np,nf)        
  complex,intent(out)         :: spec(np,nf+1) ! The +1 is for the zero frequency.
  integer :: ii,jj,indx
  integer :: ff,stat

  ! This does a Cholesky factorization for each frequency.
  ! A Cholesky factorization *is* Veers84's equation 7, it converts the cross-spectral
  ! matrix Sij to Veers' H matrix.
  !$omp parallel
  DO ff=1,nf
     CALL SPPTRF('L',np,Sij(:,ff),stat) ! Cholesky Factorization
     !$print *, stat
  ENDDO
  !$omp parallel

  spec(:,:)=0
  indx=0 ! Index for the lower-triangular matrix Sij (i.e. Veers84 'H').
  DO jj=1,np
     DO ii=jj,np
        indx=indx+1
        ! The first column needs to be zeros (for numpy.irfft; zero at the zero frequency); i.e. the '2:'.
        spec(ii,2:)=spec(ii,2:)+Sij(indx,:)*phr(jj,:) ! Multiply the columns of the H matrix (Sij) by the random phases (phr) and sum the rows.
     ENDDO
  ENDDO
  ! Note that we can sum the spectra (rather than the timeseries' as in Veers84) because 
  ! the Fourier Transform is a linear operation.  This reduces the number of inverse FFTs computed by n_p-1.
  RETURN
end subroutine veers84


subroutine ieccoh(Sij,Sii,f,y,z,uhub,a,Lc,nf,ny,nz)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "IECCOH" :: IECCOH
!DEC$ ATTRIBUTES REFERENCE :: SIJ,SII,F,Y,Z,UHUB,A,LC,NF,NY,NZ
  implicit none
  real,intent(out)      :: Sij(ny*nz*(ny*nz+1)/2,nf)
  real,intent(in)       :: Sii(ny*nz,nf),f(nf),y(ny),z(nz),uhub,a,Lc
  integer, intent(in)   :: nf,ny,nz
  integer       :: ind,ii,jj,iz(ny*nz),iy(ny*nz)
  real          :: r, ftmp(nf), Sii_sqrt(ny*nz,nf)

  DO ii=1,ny*nz ! The arrays are in fortran order.
     iz(ii)=mod(ii-1,ny)+1
     iy(ii)=(ii-1)/ny+1
  ENDDO

  ind=0
  ftmp=SQRT((f/uhub)**2+(0.12/Lc)**2)
  Sii_sqrt=SQRT(Sii)
  DO jj=1,ny*nz
     DO ii=jj,ny*nz
        ind=ind+1
        if (ii==jj) THEN
           Sij(ind,:)=Sii(ii,:)
        ELSE
           r=SQRT( (y( iy(ii) )-y( iy(jj) ))**2+( z(iz(ii)) - z( iz(jj) ))**2 )
           Sij(ind,:)=EXP(-1*a*r*ftmp)*Sii_sqrt(ii,:)*Sii_sqrt(jj,:)
        ENDIF
     ENDDO
  ENDDO

  RETURN

end subroutine ieccoh

subroutine nonIECcoh(Sij,Sii,f,y,z,u,coefs,coefExp,nf,ny,nz)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "NONIECCOH" :: NONIECCOH
!DEC$ ATTRIBUTES REFERENCE :: SIJ,SII,F,Y,Z,U,COEFS,COEFEXP,NF,NY,NZ
  implicit none
  real,intent(out)    :: Sij(ny*nz*(ny*nz+1)/2,nf)
  real,intent(in)     :: Sii(ny*nz,nf),f(nf)
  real,intent(in)     :: coefs(2),coefExp
  real,intent(in)     :: y(ny), z(nz), u(ny*nz)
  integer, intent(in) :: nf, ny, nz
  integer             :: ii, jj, ind, np
  integer             :: iy(ny*nz), iz(ny*nz)
  real                :: r, um, zm, ftmp(nf), tmpcoefs(2), Sii_sqrt(ny*nz,nf)
  np=ny*nz

  DO ii=1,np ! The arrays are in fortran order.
     iz(ii)=mod(ii-1,ny)+1
     iy(ii)=(ii-1)/ny+1
  ENDDO

  ind=0
  ftmp=f**2
  tmpcoefs(1)=-1*coefs(1)
  tmpcoefs(2)=coefs(2)**2
  Sii_sqrt=SQRT(Sii)
  DO jj=1,np ! The packmat (Sij) needs to be in column order for lapack's SPPTRF.
     DO ii=jj,np
        ind=ind+1
        if ( ii == jj ) THEN
           Sij(ind,:)=Sii(ii,:)
        ELSE
           r=SQRT ( (y( iy(ii) )-y( iy(jj) ))**2+( z(iz(ii)) - z( iz(jj) ))**2 )
           um=((u(ii)+u(jj))/2.)**2
           zm=(z(iz(ii))+z(iz(jj)))/2.
           Sij(ind,:)=EXP(tmpcoefs(1)*(r/zm)**coefExp*r*SQRT(ftmp/um+tmpcoefs(2)))*Sii_sqrt(ii,:)*Sii_sqrt(jj,:)
        ENDIF
     ENDDO
  ENDDO

  RETURN
end subroutine nonIECcoh
