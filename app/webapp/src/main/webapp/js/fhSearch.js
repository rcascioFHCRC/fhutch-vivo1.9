$(document).ready(function () {

       $('#filter-search-nav li').each(function(index){
           $(this).click(function(ev){

               $('a.active').removeClass('active');
               $(this).addClass('active');

           });

       });
});
