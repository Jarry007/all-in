var a = document.getElementById('blog_text');
var imgs = document.getElementById("blog_text").getElementsByTagName("img");
for(var i=0;i<imgs.length;i++){
	if(imgs[i].width>a.offsetWidth){
		imgs[i].width=a.offsetWidth
}
}