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
        formattedDate: function (date) {
            const d = new Date(date)
            function leadZero(n) {
              if(n <= 9){
                return "0" + n;
              }
              return n
            }
            return `${leadZero(d.getDate())}-${leadZero(d.getMonth())}-${d.getFullYear()} @ ${leadZero(d.getHours())}:${leadZero(d.getMinutes())}`
        },
        deleteDataset: function () {
            fetch(`/api/datasets/${this.dataset.id}`, {
                method: 'DELETE',
            })
            .then(response => response.json())
            .then(result => {
                this.$parent.fetchDatasets("1")
            })
        },
        // editDataset: function () {
        //     fetch(`/datasets/${this.dataset.id}`, {
        //     .then(response => response.json())
        //     .then(result => {
        //             // console.log('opened dataset editor')
        //         }
        // }),
    },
}
