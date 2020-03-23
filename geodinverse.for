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


        function to_radian(degree) result (rad)
          ! degrees to radians
          real,intent(in) :: degree
          real, parameter :: deg_to_rad = atan(1.0)/45 ! exploit intrinsic atan to generate pi/180 runtime constant
          real :: rad
 
          rad = degree*deg_to_rad
        end function to_radian
 
        subroutine haversine(deglat1,deglon1,deglat2,deglon2, dist)
          ! great circle distance -- adapted from Matlab 
          real,intent(in) :: deglat1,deglon1,deglat2,deglon2
          real :: a,c,dlat,dlon,lat1,lat2
          real, intent(out) :: dist
          real,parameter :: radius = 6370.433 
 
          dlat = to_radian(deglat2-deglat1)
          dlon = to_radian(deglon2-deglon1)
          lat1 = to_radian(deglat1)
          lat2 = to_radian(deglat2)
          a = (sin(dlat/2))**2 + cos(lat1)*cos(lat2)*(sin(dlon/2))**2
          c = 2*asin(sqrt(a))
          dist = radius*c
        end subroutine haversine
