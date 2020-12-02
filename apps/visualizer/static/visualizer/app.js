const router = new VueRouter({
    mode: 'history',
    routes: navLinks
})

new Vue({
    router,
    el: "#app",
    components: {
        navbar: () => import(staticFiles + "vue/navbar.js"),
    }
})
