<template>
  <div>
    <line-chart v-if="datacollection.labels.length" :data="datacollection" :options="options"/>
    <div v-else class="text-muted small">Sem dados para exibir no gráfico.</div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  name: 'AtivoHistoricoChart',
  components: {
    'line-chart': Line
  },
  props: {
    historico: {
      type: Array,
      required: true
    }
  },
  computed: {
    datacollection() {
      // Garantir que data é string e logar para depuração
      const labels = this.historico.map(item => {
        const str = typeof item.data === 'string' ? item.data : String(item.data)
        return str
      })
      const data = this.historico.map(item => Number(item.preco_fechamento))
      // Log para depuração
      if (process.env.NODE_ENV !== 'production') {
        console.log('Gráfico - labels:', labels)
        console.log('Gráfico - data:', data)
      }
      return {
        labels,
        datasets: [
          {
            label: 'Preço de Fechamento',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            data,
            fill: false,
            tension: 0.1
          }
        ]
      }
    },
    options() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Data'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Preço (R$)'
            },
            beginAtZero: false
          }
        },
        plugins: {
          legend: {
            display: true
          },
          tooltip: {
            enabled: true
          }
        }
      }
    }
  },
  watch: {
    historico: {
      handler() {
        this.$forceUpdate()
      },
      deep: true
    }
  }
}
</script>

<style scoped>
div {
  min-height: 300px;
  height: 350px;
}
</style>