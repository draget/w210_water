        subroutine geo_dist(lat1, lon1, lat2, lon2, s12)

            include 'geodesic.inc'

            real*8, intent(in) ::  lat1, lon1, lat2, lon2 

            real*8 :: a, f, azi1, azi2, 
     +          dummy1, dummy2, dummy3, dummy4, dummy5

            real*8, intent(out) :: s12

            integer :: omask

*           WGS84 values
            a = 6378137d0
            f = 1/298.257223563d0

            omask = 0

            call invers(a, f, lat1, lon1, lat2, lon2,
     +          s12, azi1, azi2, omask,
     +          dummy1, dummy2, dummy3, dummy4, dummy5)

            s12 = s12/1000

        end subroutine geo_dist

