var open = false;
var full_size = [];
var collapsed_icons = [];


function Init_Nav(){
    //find all nav links
    
    var link_list = document.getElementsByTagName('a')
    for (i in link_list){
        if((link_list[i].className).indexOf("nav-open") > -1){
            full_size.push(link_list[i]);
        }
        if((link_list[i].className).indexOf("nav-closed") > -1){
            collapsed_icons.push(link_list[i]);
        }
    }
    
    

}

function Expand_Nav() {

    // flip flop for opening sidebar
    if (open == true) {
    open = false;
    var navbar = document.getElementById("navbar");

    navbar.style.width = "10vw";

    for (i in full_size){
        full_size[i].style.display = 'none';
    }
    for (i in collapsed_icons){
        collapsed_icons[i].style.display = 'block';
    }

    }
    else if (open == false) {
    open = true;
    var navbar = document.getElementById("navbar");

    navbar.style.width = "25vw";

    for (i in full_size){
        full_size[i].style.display = 'block';
    }
    for (i in collapsed_icons){
        collapsed_icons[i].style.display = 'none';
    }

  } 
}