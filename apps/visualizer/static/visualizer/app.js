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
