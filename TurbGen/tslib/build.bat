REM This command compiles the 'tslib' library in windows.
REM Compilation of the lib requires python and the 'minGW' program-suite.
REM Once minGW is properly installed you will also need to configure your system.
REM ADD "<mingw-install-path>\bin;<python-install-path\Scripts\" to your system path ('path' Environmental Variable).
REM Also add '.py' to your 'PATHEXT' environment variable.

f2py --overwrite-signature -m tslib -h tslib.pyf tslib.f95

f2py --compiler=mingw32 -lgomp -m tslib -c tslib.f95 lapack\lsame.f lapack\xerbla.f lapack\sdot.f lapack\sscal.f lapack\sspr.f lapack\stpsv.f lapack\spptrf.f

REM I've tried to use the intel compiler, but haven't been able to get it to work.
REM f2py --fcompiler=intelv -m tslib -c tslib.f95 lapack\lsame.f lapack\xerbla.f lapack\sdot.f lapack\sscal.f lapack\sspr.f lapack\stpsv.f lapack\spptrf.f

copy tslib.pyd ..\
