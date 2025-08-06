<template>
  <div>
    <b-form-group label="Filtros" label-for="search-input" class="mb-3">
      <b-form-input
        id="search-input"
        v-model="search"
        placeholder="Buscar ativos por código, nome, etc..."
        @keyup.enter="fetchAtivos"
        trim
      />
    </b-form-group>

    <b-row class="mb-3">
      <b-col cols="4">
        <b-form-select
          v-model="selectedSetor"
          :options="setorOptions"
          @change="fetchAtivos"
          class="mb-2"
        >
          <template #first>
            <option value="">Todos os Setores</option>
          </template>
        </b-form-select>
      </b-col>

      <b-col cols="4">
        <b-form-select
          v-model="selectedSegmento"
          :options="segmentoOptions"
          @change="fetchAtivos"
          class="mb-2"
        >
          <template #first>
            <option value="">Todos os Segmentos</option>
          </template>
        </b-form-select>
      </b-col>

      <b-col cols="4" class="d-flex align-items-center">
        <b-button variant="primary" @click="fetchAtivos" :disabled="loading">
          Buscar
        </b-button>
        <b-spinner small label="Carregando..." v-if="loading" class="ml-3" />
      </b-col>
    </b-row>

    <b-table
      :items="filteredAtivos"
      :fields="fields"
      striped
      hover
      responsive
      :busy="loading"
      small
      class="mb-3"
      :empty-text="'Nenhum ativo encontrado.'"
    >
      <template #cell(acoes)="data">
        <b-button size="sm" variant="success" @click="$emit('adicionar-acao', data.item)">
          Adicionar
        </b-button>
      </template>
    </b-table>

    <b-pagination
      v-model="currentPage"
      :total-rows="totalRows"
      :per-page="perPage"
      aria-controls="table"
      @change="onPageChange"
      class="justify-content-center"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { BFormInput, BFormGroup, BFormSelect, BButton, BSpinner, BTable, BPagination, BRow, BCol } from 'bootstrap-vue'

export default {
  components: {
    BFormInput,
    BFormGroup,
    BFormSelect,
    BButton,
    BSpinner,
    BTable,
    BPagination,
    BRow,
    BCol
  },
  data() {
    return {
      ativos: [],
      filteredAtivos: [],
      search: '',
      setores: [],
      segmentos: [],
      selectedSetor: '',
      selectedSegmento: '',
      apiUrl: '/api/ibovespa/ativos/',
      totalRows: 0,
      perPage: 10,
      currentPage: 1,
      loading: false,
      fields: [
        { key: 'codigo', label: 'Código', sortable: true },
        { key: 'nome', label: 'Nome', sortable: true },
        { key: 'setor', label: 'Setor', sortable: true },
        { key: 'segmento', label: 'Segmento', sortable: true },
        { key: 'preco_atual', label: 'Preço Atual', sortable: true },
        { key: 'variacao', label: 'Variação (%)', sortable: true },
        { key: 'acoes', label: 'Ações' }
      ]
    }
  },
  computed: {
    ...mapGetters(['getToken', 'getDominio']),
    setorOptions() {
      return this.setores.map(setor => ({ value: setor.nome, text: setor.nome }))
    },
    segmentoOptions() {
      return this.segmentos.map(segmento => ({ value: segmento.nome, text: segmento.nome }))
    }
  },
  methods: {
    async fetchSetores() {
      try {
        const res = await fetch(`${this.getDominio}/api/ibovespa/setor/`, {
          headers: { Authorization: `Token ${this.getToken}` }
        })
        if (!res.ok) throw new Error('Erro carregando setores')
        this.setores = await res.json()
      } catch (err) {
        console.error(err)
      }
    },
    async fetchSegmentos() {
      try {
        const res = await fetch(`${this.getDominio}/api/ibovespa/segmento/`, {
          headers: { Authorization: `Token ${this.getToken}` }
        })
        if (!res.ok) throw new Error('Erro carregando segmentos')
        this.segmentos = await res.json()
      } catch (err) {
        console.error(err)
      }
    },
    async fetchAtivos() {
      this.loading = true
      const params = []
      if (this.search && this.search.trim() !== '') {
        params.push(`search=${encodeURIComponent(this.search)}`)
      }
      if (this.selectedSetor && this.selectedSetor.trim() !== '') {
        params.push(`setor=${encodeURIComponent(this.selectedSetor)}`)
      }
      if (this.selectedSegmento && this.selectedSegmento.trim() !== '') {
        params.push(`segmento=${encodeURIComponent(this.selectedSegmento)}`)
      }

      let fetchUrl = `${this.getDominio}${this.apiUrl}`
      if (params.length > 0) {
        fetchUrl += `?${params.join('&')}`
      }

      try {
        const res = await fetch(fetchUrl, {
          headers: { Authorization: `Token ${this.getToken}` }
        })
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
        const data = await res.json()
        this.ativos = data
        this.totalRows = data.count
        this.filteredAtivos = data
      } catch (error) {
        console.error('Erro ao buscar ativos:', error)
      } finally {
        this.loading = false
      }
    },
    onPageChange(page) {
      this.fetchAtivos(page)
    }
  },
  mounted() {
    this.fetchSetores()
    this.fetchSegmentos()
    this.fetchAtivos()
  },
  watch: {
    selectedSetor() {
      this.currentPage = 1
      this.fetchAtivos()
    },
    selectedSegmento() {
      this.currentPage = 1
      this.fetchAtivos()
    }
  }
}
</script>

<style scoped>
.mb-3 {
  margin-bottom: 1rem;
}
.ml-3 {
  margin-left: 1rem;
}
</style>