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
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "NONIECCOH" :: NONIECCOH
!DEC$ ATTRIBUTES REFERENCE :: PHR,F,Y,Z,U,COEF_A,COEF_B,COEFEXP,NCORE,NF,NY,NZ
  use omp_lib
  implicit none
  complex,intent(inout) :: phr(ny*nz,nf)
  real,intent(in)     ::  f(nf), y(ny), z(nz), u(ny*nz)
  real,intent(in)     :: coef_a,coef_b,coefExp
  integer, intent(in) :: ncore, nf, ny, nz
  complex             :: phr_tmp(ny*nz,nf)
  integer             :: ii, jj, ff, ind, stat, ntot, np, jj1!, ind2
  integer             :: iz
!  real(4)        :: tmp
!  real(4)                :: 
  real(4),allocatable  :: work(:), um(:), r(:), tmpz(:)
  real(4)                :: tmp_b,ftmp(nf)
  DOUBLE PRECISION :: tm0,tm1,tm2,tm3,tm,tmr1,tmr2,tmr3,tmr_tmp0,tmr_tmp1
!  real(4)    :: ftmp(nf)
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
!!$  ind=indx(4,2,np)
!!$  print *, ind
  !ind=20
  !print *, tmpz(ind)
  
  !print *, z(2),y(2),r(ind),um(ind),((r(ind)/tmpz(ind))**coefexp),ftmp(10)
  !print *, u((10-1)*ny+ny/2),coef_a,coef_b
  
  tmp_b=coef_b**2
  !print *, 'start coh'
  IF (coefExp/=0) THEN
     tmpz=-1.0*coef_a*r*(r/tmpz)**coefExp
  ELSE
     tmpz=-1.0*coef_a*r
  ENDIF
  !print *, tmpz(ind)*sqrt((ftmp(10)/um(ind))**2+tmp_b)
  tmr1=0
  tmr2=0
  tmr3=0
  tmr_tmp0=0
  tmr_tmp1=0
  !print *, ny,nz,nf
  !$omp parallel private(ii, jj, ff, ind, work, r, stat) default(shared)
  !$omp do schedule( dynamic )
  DO ff=1,nf
     call cpu_time(tm0)
!!$     DO ii=1,np
!!$        DO JJ=1,II
!!$     DO JJ=1,np
!!$        DO ii=jj,np
!!$           !JJ1       = JJ - 1
!!$           ind      = np*(JJ-1) - JJ*(JJ-1)/2 + II   !Index of matrix ExCoDW (now Matrix), coherence between points I & J
!!$           work(ind)=EXP(tmpz(ind)*SQRT((ftmp(ff)/um(ind))**2+tmp_b)) ! r*SQRT(f**2/u_mean**2+coef_b**2)
!!$           iz=iz+1
!!$        ENDDO
!!$     ENDDO
     !IF ( tmp_b/=0 ) THEN
        work=tmpz*SQRT((f(ff)/um)**2+tmp_b)
!!$        !call cpu_time(tm)
!!$        !tmr_tmp0=tmr_tmp0-tm0+tm
        work=EXP(work) ! r*SQRT(f**2/u_mean**2+coef_b**2)
!!$        !call cpu_time(tm)
!!$        !tmr_tmp1=tmr_tmp1-tm0+tm
!!$     ELSE
        !work=(tmpz/um)*f(ff)
        !call cpu_time(tm)
        !tmr_tmp0=tmr_tmp0-tm0+tm
!!$        work=EXP((tmpz/um)*f(ff))
        !call cpu_time(tm)
        !tmr_tmp1=tmr_tmp1-tm0+tm
!!$     ENDIF
     call cpu_time(tm1)
     CALL SPPTRF('L',np,work,stat)
     call cpu_time(tm2)
     DO ii=1,np
        ! 'ompsingle' directive unnecessary b/c parallel only applies to the outer loop.
        !jj=indx(ii,1,np)
        !ind=indx(ii,ii,np)
        !phr(ii,ff+1)=sum(work(jj:ind)*phr_tmp(jj:ind,ff),1) ! THIS IS VERY SLOW
        DO jj=1,ii
           phr(ii,ff)=phr(ii,ff)+work(indx(ii,jj,np))*phr_tmp(jj,ff) ! Multiply the columns of the H matrix (Sij) by the random phases (phr_tmp) and sum the rows.
        ENDDO
     ENDDO
     call cpu_time(tm3)
     tmr1=tmr1+tm1-tm0
     tmr2=tmr2+tm2-tm1
     tmr3=tmr3+tm3-tm2
  ENDDO
  !phr(:,:)=tmpphr(:,:)
  !$omp end do
  !$omp end parallel
  !print *, tmr_tmp0,tmr_tmp1
  !print *, tmr1,tmr2,tmr3
  !print *, iz
  RETURN
end subroutine nonIECcoh

subroutine IECcoh(phr,f,y,z,uhub,a,Lc,ncore,nf,ny,nz)
!DEC$ ATTRIBUTES DLLEXPORT, DECORATE, ALIAS : "NONIECCOH" :: NONIECCOH
!DEC$ ATTRIBUTES REFERENCE :: PHR,F,Y,Z,U,COEF_A,COEF_B,COEFEXP,NCORE,NF,NY,NZ
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
  !real(KIND=DP) :: tm0,tm1!,tm2,tmr1,tmr2
  !DOUBLE PRECISION :: tm0,tm1!,tm2,tmr1,tmr2
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
