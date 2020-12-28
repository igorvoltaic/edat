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
        deleteDataset: function (event) {
            event.preventDefault();
            event.stopPropagation();
            fetch(`/api/dataset/${this.dataset.id}`, {
                method: 'DELETE',
            })
            .then(() => {
                this.$parent.fetchDatasets("1")
            })
        },
        openDataset: function() {
            router.push({ name: 'dataset', params: { id: this.dataset.id } })
        },
        editDataset: function(event) {
            event.preventDefault();
            event.stopPropagation();
            router.push({
                name: 'editor',
                params: {
                    id: this.dataset.id,
                    result: null,
                    new_dataset: false,
                },
            });
         },
    },
}
