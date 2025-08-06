<template>
  <div class="home">
    <h1>Tabela Base - Ibovespa</h1>
    <p class="text-muted">Visualize e filtre todas as ações disponíveis no mercado brasileiro</p>
    <AtivosTable @adicionar-acao="adicionarAcaoUsuario" />
  </div>
</template>

<script>
import AtivosTable from '@/components/ibovespa/AtivosTable.vue'

export default {
  components: {
    AtivosTable
  },
  methods: {
    async adicionarAcaoUsuario(acaoBase) {
      // Aqui você pode implementar a lógica para adicionar uma ação,
      // similar ao que você já tinha no exemplo com fetch para seu backend.
      console.log('Adicionar ação:', acaoBase)
      // Exemplo: chamar uma API para salvar ação, com token e headers
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
}
h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  text-align: center;
}
p {
  text-align: center;
  margin-bottom: 30px;
  color: #6c757d;
}
</style>
