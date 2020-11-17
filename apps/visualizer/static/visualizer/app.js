const router = new VueRouter({
    routes: navLinks
})

new Vue({
    router,
    el: "#app",
    components: {
        navbar: () => import(staticFiles + "vue/navbar.js"),
    }
})


document.addEventListener('DOMContentLoaded', function() {

    // when a file selected for upload substitute a
    // label's inner html for filename
    document.querySelectorAll('#upload-csv-file').forEach(upload => {
        upload.onchange = () => {
            upload.previousElementSibling.innerHTML = upload.files[0].name
        };
    });
})
