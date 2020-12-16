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
        openDataset: function(datasetId) {
            router.push({ name: 'dataset', params: { id: datasetId } })
        },
        editDataset: function(event) {
            event.preventDefault();
            event.stopPropagation();
            fetch(`/api/dataset/${this.dataset.id}`)
            .then(response => {
                if (response.status !== 200) {
                    throw new Error('Dataset not found');
                }
                return response.json()
            })
            .then(result => {
                router.push({
                    name: 'editor',
                    params: {
                        result: result,
                        new_dataset: false,
                    },
                });
            })
            .catch(ex => {
                console.log(ex.message);
            })
         },
    },
}
