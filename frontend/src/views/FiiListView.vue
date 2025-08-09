<template>
  <div class="container py-3">
    <h3 class="mb-3">Fundos Imobiliários</h3>
    <FiiTable />
  </div>
</template>

<script>
import FiiTable from '@/components/ibovespa/FiiTable.vue'

export default {
  components: { FiiTable }
}
</script>

<style scoped>
.container { padding-top: 20px; }
</style>


