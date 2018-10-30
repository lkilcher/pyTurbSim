program testtslib

use tslib

implicit None
integer :: nf,nz,ny,ncore
integer :: ff,ii,jj,ind
character(len=32) :: arg
real,allocatable :: z(:),y(:)
real,allocatable :: f(:),u(:)
complex,allocatable :: spec(:,:),phr(:,:)
REAL             :: coef_a,coef_b,coefExp,val
DOUBLE PRECISION :: tm0,tm1,tmr1

ncore=1
nf=6000
coef_a=0.1
coef_b=0.0
coefExp=0.0

call getarg(1,arg)
read(arg,'(i32)') nz
call getarg(2,arg)
read(arg,'(i32)') ny
call RANDOM_SEED()

allocate(spec(ny*nz,nf+1))
allocate(z(nz))
allocate(y(ny))
allocate(u(ny*nz))
allocate(f(nf))
allocate(phr(ny*nz,nf))

DO ff=1,nf
   f(ff)=ff*0.001
   DO ii=1,nz
      DO jj=1,ny
         ind=(ii-1)*ny+jj
         call RANDOM_NUMBER(val)
         phr(ind,ff)=val
      ENDDO
   ENDDO
ENDDO

DO ii=1,nz
   z(ii)=10.+ii*0.8
   DO jj=1,NY
      ind=(ii-1)*ny+jj
      u(ind)=0.1+1.3*(z(ii)/10)**0.14286
   ENDDO
ENDDO
DO ii=1,ny
   y(ii)=10.+ii*0.8
ENDDO

print *, u(10)

CALL CPU_TIME(tm0)

call nonIECcoh(spec,phr,f,y,z,u,coef_a,coef_b,coefExp,ncore,nf,ny,nz)

CALL CPU_TIME(tm1)

print *, tm1-tm0

end program testtslib
