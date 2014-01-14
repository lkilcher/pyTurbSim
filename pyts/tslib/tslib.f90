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


subroutine nonIECcoh(spec,Sii,phr,f,y,z,u,coef_a,coef_b,coefExp,ncore,nf,ny,nz)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "NONIECCOH" :: NONIECCOH
!DEC$ ATTRIBUTES REFERENCE :: SII,PHR,F,Y,Z,U,COEFS,COEFEXP,NCORE,NF,NY,NZ
  use omp_lib
  implicit none
  real,intent(in)    :: Sii(ny*nz,nf)
  complex,intent(inout) :: spec(ny*nz,nf)
  real,intent(in)     :: coef_a,coef_b,coefExp
  real,intent(in)     :: y(ny), z(nz), u(ny*nz), f(nf)
  complex,intent(in)  :: phr(ny*nz,nf)
  integer, intent(in) :: nf, ny, nz, ncore
  integer             :: ii, jj, ff, ind, np, stat!, ind2
  integer             :: iy(ny*nz), iz(ny*nz)
  real                :: r, tmp, tmp_a, tmp_b
  real                :: work(ny*nz*(ny*nz+1)/2)
  np=ny*nz

  IF (ncore > 0) THEN
     CALL OMP_SET_NUM_THREADS(ncore)
  ENDIF

  DO ii=1,np ! The arrays are in fortran order.
     iz(ii)=mod(ii-1,ny)+1
     iy(ii)=(ii-1)/ny+1
  ENDDO
  
  tmp_b=coef_b**2
  !print *, 'start coh'
  DO ff=1,nf
     DO jj=1,np ! The packmat (Sij) needs to be in column order for lapack's SPPTRF.
        DO ii=jj,np
           !ind=ind+1
           ind=indx(ii,jj,np)
           !print *, ind,ind2,jj,(jj*(jj-1))/2
           if ( ii == jj ) THEN
              work(ind)=1
           ELSE
              r=SQRT ( (y( iy(ii) )-y( iy(jj) ))**2+( z(iz(ii)) - z( iz(jj) ))**2 )
              if ( coefExp/=0 ) THEN
                 tmp_a=-1*coef_a*(2.*r/(z(iz(ii))+z(iz(jj))))**coefExp
              ELSE
                 tmp_a=-1*coef_a
              ENDIF
              IF ( tmp_b/=0 ) THEN
                 tmp=r*SQRT((f(ff)/(u(ii)+u(jj))/2.)**2+tmp_b) ! r*SQRT(f**2/u_mean**2+coef_b**2)
              ELSE
                 tmp=r*f(ff)/((u(ii)+u(jj))/2.) ! r*f/u_mean
              ENDIF
              work(ind)=EXP(tmp_a*tmp)
           ENDIF
        ENDDO
     ENDDO
     CALL SPPTRF('L',np,work,stat)
     DO ii=1,np
        ! omp'single' directive unnecessary b/c parallel only applies to the outer loop.
        DO jj=1,ii
           spec(ii,ff)=spec(ii,ff)+work(indx(ii,jj,np))*SQRT(Sii(ii,ff))*phr(jj,ff) ! Multiply the columns of the H matrix (Sij) by the random phases (phr) and sum the rows.
        ENDDO
     ENDDO
     
  ENDDO
  !print *, 'end coh'

  RETURN
end subroutine nonIECcoh

END MODULE TSLIB
