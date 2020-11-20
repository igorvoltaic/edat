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
        showId: function () {
            alert(this.dataset.id)
        },
        deleteDataset: function () {
            fetch("datasets/" + this.dataset.id, {
                method: 'DELETE',
            })
        },
        // edit-dataset: function () {
        //     fetch(`/datasets/${this.dataset.id}`, {
        //     .then(response => response.json())
        //     .then(result => {
        //             // console.log('opened dataset editor')
        //         }
        // }),
    },
}
