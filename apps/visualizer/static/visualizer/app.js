const router = new VueRouter({
    mode: 'history',
    routes: navLinks
})

new Vue({
    router,
    el: "#app",
    components: {
        navbar: () => import(staticFiles + "vue/navbar.js"),
    },
    mounted: function() {
        window.addEventListener('click', function(e) {
            for (const dropdown of document.querySelectorAll('.select-dropdown')) {
                const menu = dropdown.querySelector('.dropdown-menu')
                if (!dropdown.contains(e.target)) {
                    menu.classList.remove('select-active');
                }
            }
        });
    }
})
