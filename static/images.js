window.addEventListener("load", function () {
    for (let i of document.querySelectorAll("img")) {
        console.log(i);
        i.addEventListener("click", function (e) {
            let container = document.createElement("div")
            container.style.position = "fixed";
            container.style.height = "100%";
            container.style.width = "100%";
            container.style.zIndex = "10";
            container.style.top = "0";

            let img = document.createElement("img");
            img.src = e.target.src;
            img.style.width = "100%";
            img.style.height = "100%";
            img.style.objectFit = "contain";
            container.appendChild(img);
            img.addEventListener("click", function () {
                container.remove();
            })

            document.body.appendChild(container);
        })
    }
})