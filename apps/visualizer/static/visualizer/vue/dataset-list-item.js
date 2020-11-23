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
            fetch(`/api/datasets/${this.dataset.id}`, {
                method: 'DELETE',
            })
            .then(response => response.json())
            .then(result => {
                this.$parent.fetchDatasets("1")
            })
        },
        openDataset: function() {
            let datasetId = this.dataset.id
            router.push({ name: 'dataset', params: { id: datasetId } }) // -> /dataset/:id
        },
        editDataset: function() {
            alert('edit!');
        },
    },
}
