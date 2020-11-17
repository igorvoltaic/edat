export default {
    name: 'dataset-list-item',
    delimiters: ['[[',']]'],
    template: '#dataset-list-item-template',
    props: ['dataset'],
    data() {
        return {
            currentUser: currentUser,
            auth: auth
        }
    },
    methods: {
        del-dataset: function () {
            fetch(`/datasets/${this.dataset.id}`, {
                method: 'DELETE',
                credentials: 'same-origin',
                headers: {
                    "X-CSRFToken": csrf_token
                },
            })
        },
        edit-dataset: function () {
            fetch(`/datasets/${this.dataset.id}`, {
            .then(response => response.json())
            .then(result => {
                    // console.log('opened dataset editor')
                }
            })
        },
    }
}
