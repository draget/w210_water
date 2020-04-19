function getcallback(div_id) {

    return function() {

            element = document.getElementById(div_id);

              var event = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
              });
           element.dispatchEvent(event);


            };
}



divs = document.getElementsByTagName('div');

for (var div of divs) {

    if(div.id.search('dynlabel') > 0 || div.id.search('dynslider') > 0) {

        div.onmouseover = getcallback(div.id);

    }

}


