
var updateBtns = document.getElementsByClassName('update-cart');

for(var i=0 ;i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click',function(){
        var productID = this.dataset.product;
        var action = this.dataset.action;
        var page = this.dataset.page;
        console.log('productID= ',productID,"action =",action);
        console.log("User:",user)
        updateUserOrder(productID,action)
        reload();
        
    });
}

function reload(){
    var time = 0;

    var timer = setInterval(function(){
        time +=0.5
        console.log( time +" seconds have passed");
        location.reload()
        clearInterval(timer);
    },100);
}

function updateUserOrder(productID,action){
    console.log("User logged in , sending data ...")
    var url = '/update_item/'

    fetch(
        url,{
            method:'POST',
            headers:{
                'Content-type':'application/json',
                'X-CSRFToken':csrftoken
            },
            body:JSON.stringify({"productID":productID,"action":action})
        }
    )

    .then((response)=>{
        return response.json()
    })
    .then((data)=>{
        console.log("DATA:",data)
        
    }) 
}

function opennav(){
    var h =document.getElementById("fakenavbar").style.height
    if(h=="56px"){
        document.getElementById("fakenavbar").style.height="185px";
        document.getElementsByClassName("cart-item-sm")[0].style.display="none"
        document.getElementsByClassName("cart-item-lg")[0].style.display="inline-block"
    }
    else{
        document.getElementById("fakenavbar").style.height="56px";
        document.getElementsByClassName("cart-item-sm")[0].style.display="inline-block"
        document.getElementsByClassName("cart-item-lg")[0].style.display="none"
    }
    
}


