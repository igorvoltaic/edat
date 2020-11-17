export default {
    delimiters: ['[[', ']]'],
    template: '#navbar-link-template',
    props: ['link'],
    data() {
        return {
            currentUser: currentUser,
            auth: auth
        }
    }
}
