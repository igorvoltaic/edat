const router = new VueRouter({
    mode: 'history',
    routes: navLinks
})

const dropdownSelect = {
  mounted() {
      document.querySelectorAll(".select-dropdown").forEach(dropdown => {
          dropdown.children[2].addEventListener('click', function() {
              this.parentElement.querySelector('.dropdown-menu').classList.toggle('select-active');
          })
          dropdown.children[1].addEventListener('click', function() {
              this.parentElement.querySelector('.dropdown-menu').classList.toggle('select-active');
          })
      });

      window.addEventListener('click', function(e) {
          for (const dropdown of document.querySelectorAll('.select-dropdown')) {
              const menu = dropdown.querySelector('.dropdown-menu')
              if (!dropdown.contains(e.target)) {
                  menu.classList.remove('select-active');
              }
          }
      });
  }
}

new Vue({
    router,
    el: "#app",
    components: {
        navbar: () => import(staticFiles + "vue/navbar.js"),
    },
})
