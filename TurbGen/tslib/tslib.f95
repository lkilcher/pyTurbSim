MODULE tslib

CONTAINS

FUNCTION INDX(ii,jj,np)
  ! Returns the 'lower triangular' index for an np x np array.
  !
  ! indx is equivalent to:
  ! indx=0
  ! DO jj=1,np
  !   DO ii=jj,np
  !     indx=indx+1
  !     <SOME CODE>
  !   ENDDO
  ! ENDDO
  integer :: ii,jj
  integer :: np
  integer :: indx
  IF (jj>ii) THEN
     ! THIS SWAPS ii AND jj VARIABLES WITHOUT A TEMPORARY VARIABLE.
     ii=ii+jj
     jj=ii-jj
     ii=ii-jj
  ENDIF
  indx=(jj-1)*np+ii-(jj*(jj-1))/2
  RETURN
END FUNCTION INDX

FUNCTION r_arr(y,z,ny,nz)
  integer,intent(in) :: ny,nz
  real,intent(in)    :: y(ny),z(nz)
  integer            :: ii,jj
  real,dimension(ny*nz*(ny*nz+1)/2) :: r_arr
  integer            :: iz(nz*ny),iy(nz*ny)

  DO ii=1,ny*nz 
     ! The spatial (z,y) indexes are in C order.
     ! This needs to be consistent with the reshape, sub2ind, ind2sub,
     ! and flatten methods in the tsGrid class.
     iy(ii)=mod(ii-1,ny)+1
     iz(ii)=(ii-1)/ny+1
!!$     ! Fortran order
!!$     iz(ii)=mod(ii-1,nz)+1
!!$     iy(ii)=(ii-1)/nz+1
  ENDDO

  DO jj=1,ny*nz ! The packmat (Sij) needs to be in column order for lapack's SPPTRF.
     DO ii=jj,ny*nz
        ind=indx(ii,jj,ny*nz)
        IF (ii==jj) THEN
           r_arr(ind)=0
        ELSE
           r_arr(ind)=(y( iy(ii) )-y( iy(jj) ))**2+( z(iz(ii)) - z( iz(jj) ))**2
        ENDIF
     ENDDO
  ENDDO
  r_arr=SQRT(r_arr)
  RETURN

END FUNCTION r_arr

subroutine nonIECcoh(phr,f,y,z,u,coef_a,coef_b,coefExp,ncore,nf,ny,nz)
  use omp_lib
  implicit none
  complex,intent(inout) :: phr(ny*nz,nf)
  real,intent(in)     ::  f(nf), y(ny), z(nz), u(ny*nz)
  real,intent(in)     :: coef_a,coef_b,coefExp
  integer, intent(in) :: ncore, nf, ny, nz
  complex             :: phr_tmp(ny*nz,nf)
  integer             :: ii, jj, ff, ind, stat, ntot, np!, jj1!, ind2
  integer             :: iz
  real(4),allocatable  :: work(:), um(:), r(:), tmpz(:)
  real(4)                :: tmp_b,ftmp(nf)
  np=ny*nz
  ntot=(np*(np+1))/2
  phr_tmp=phr
  phr(:,:)=0
  
  allocate(r(ntot))
  allocate(tmpz(ntot))
  allocate(um(ntot))
  allocate(work(ntot))
  iz=0

  IF (ncore > 0) THEN
     CALL OMP_SET_NUM_THREADS(ncore)
  ENDIF

  r=r_arr(y,z,ny,nz)
  ftmp=f

  DO ii=1,np
     DO jj=1,ii
        ind=indx(ii,jj,np)
        um(ind)=(u(ii)+u(jj))/2
!!$        tmpz(ind)=(z(mod(ii-1,nz)+1)+z(mod(jj-1,nz)+1))/2 ! Fortran ordering of space
        tmpz(ind)=(z((ii-1)/ny+1)+z((jj-1)/ny+1))/2 ! C ordering of spatial vars (matches O-TurbSim)
     ENDDO
  ENDDO
  
  tmp_b=coef_b**2
  IF (coefExp/=0) THEN
     tmpz=-1.0*coef_a*r*(r/tmpz)**coefExp
  ELSE
     tmpz=-1.0*coef_a*r
  ENDIF

  !$omp parallel private(ii, jj, ff, work, stat) default(shared)
  !$omp do schedule( dynamic )
  DO ff=1,nf
     ! Calculate the coherence for this spectral model.
     IF (tmp_b==0) THEN
        work=EXP(tmpz*f(ff)/um)
     ELSE
        work=EXP(tmpz*SQRT((f(ff)/um)**2+tmp_b))
     ENDIF
     ! Perform the Cholesky Factorization (Veers 1984 decomposition)
     CALL SPPTRF('L',np,work,stat)
     DO ii=1,np
        DO jj=1,ii
            ! Multiply the columns of the H matrix (Sij) by the random phases (phr_tmp) and sum the rows.
           phr(ii,ff)=phr(ii,ff)+work(indx(ii,jj,np))*phr_tmp(jj,ff)
        ENDDO
     ENDDO
  ENDDO
  !$omp end do
  !$omp end parallel
  RETURN
end subroutine nonIECcoh

subroutine IECcoh(phr,f,y,z,uhub,a,Lc,ncore,nf,ny,nz)
  use omp_lib
  implicit none
  complex,intent(inout) :: phr(ny*nz,nf)
  real,intent(in)       :: f(nf),y(ny),z(nz),uhub,a,Lc
  integer, intent(in)   :: nf, ny, nz, ncore
  complex               :: phr_tmp(ny*nz,nf)
  real                  :: ftmp(nf)
  integer               :: ii, jj, ff, np, stat!, ind2
  real                  :: r(ny*nz*(ny*nz+1)/2)
  real                  :: work(ny*nz*(ny*nz+1)/2)
  np=ny*nz
  phr_tmp=phr
  phr(:,:)=0

  IF (ncore > 0) THEN
     CALL OMP_SET_NUM_THREADS(ncore)
  ENDIF

  r=r_arr(y,z,ny,nz)
  
  ftmp=-1*a*SQRT((f/uhub)**2+(0.12/Lc)**2)
  !$omp parallel private(ii, jj, ff, work, stat) default(shared)
  !$omp do schedule( dynamic )
  DO ff=1,nf
     work=EXP(r*ftmp(ff))
     CALL SPPTRF('L',np,work,stat)
     DO ii=1,np
        ! omp'single' directive unnecessary b/c parallel only applies to the outer loop.
        DO jj=1,ii
           phr(ii,ff)=phr(ii,ff)+work(indx(ii,jj,np))*phr_tmp(jj,ff) ! Multiply the columns of the H matrix (Sij) by the random phases (phr) and sum the rows.
        ENDDO
     ENDDO
     
  ENDDO
  !$omp end do
  !$omp end parallel

  RETURN
end subroutine IECcoh

END MODULE TSLIB
