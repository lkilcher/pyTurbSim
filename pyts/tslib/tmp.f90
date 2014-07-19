  !$omp parallel private(ii , jj, r, ind, tmp_a, tmp )&
  !$omp default( shared )
  !$omp do schedule( dynamic )
  DO jj=1,np ! The packmat (Sij) needs to be in column order for lapack's SPPTRF.
     DO ii=jj,np
        ind=(jj-1)*(np+1)+ii-jj+1-(jj*(jj-1))/2
        if ( ii == jj ) THEN
           Sij(ind,:)=Sii(ii,:)
        ELSE
           r=SQRT ( (y( iy(ii) )-y( iy(jj) ))**2+( z(iz(ii)) - z( iz(jj) ))**2 )
           IF ( CoefExp /=0. ) THEN
              tmp_a=-1*coef_a*(2.*r/(z(iz(ii))+z(iz(jj))))**coefExp
           ENDIF
           IF ( tmp_b==0. ) THEN
              tmp=(tmp_a*2*r/(u(ii)+u(jj)))*f
           ELSE
              tmp=(tmp_a*r)*SQRT(f2/((u(ii)+u(jj))/2.)**2+tmp_b)
           ENDIF
           Sij(ind,:)=EXP(tmp)*Sii_sqrt(ii,:)*Sii_sqrt(jj,:)
        ENDIF
     ENDDO
  ENDDO
  !$omp end do
  !$omp end parallel
  !print *, 'end coh'
