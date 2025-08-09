<template>
  <div>
    <b-card class="shadow-lg p-4">
      <b-form-group label="Filtros" label-for="fii-search-input" class="mb-3">
        <b-form-input
          id="fii-search-input"
          v-model="search"
          placeholder="Buscar por código, nome, segmento..."
          @keyup.enter="fetchFiis"
          trim
        />
      </b-form-group>

      <b-row class="mb-3">
        <b-col cols="6">
          <b-form-select
            v-model="selectedSegmento"
            :options="segmentoOptions"
            @change="fetchFiis"
            class="mb-2"
          >
            <template #first>
              <option value="">Todos os Segmentos</option>
            </template>
          </b-form-select>
        </b-col>
        <b-col cols="6" class="d-flex align-items-center justify-content-end">
          <b-button variant="primary" @click="fetchFiis" :disabled="loading">
            <b-icon icon="search" class="mr-1" /> Buscar
          </b-button>
          <b-spinner small label="Carregando..." v-if="loading" class="ml-3" />
        </b-col>
      </b-row>

      <b-table
        :items="fiis"
        :fields="fields"
        striped hover responsive small
        :busy="loading"
        :empty-text="'Nenhum FII encontrado.'"
      >
        <template #cell(cotacao_atual)="{ item }">
          {{ formatarDinheiro(item.cotacao_atual) }}
        </template>
        <template #cell(dividend_yield_percent)="{ item }">
          {{ formatarPercentual(item.dividend_yield_percent) }}
        </template>
        <template #cell(liquidez_media_diaria)="{ item }">
          {{ item.liquidez_media_diaria ? item.liquidez_media_diaria.toLocaleString('pt-BR') : '-' }}
        </template>
        <template #cell(acoes)="{ item }">
          <b-button size="sm" variant="info" @click="abrirDetalhes(item.codigo)">
            <b-icon icon="info-circle" /> Detalhes
          </b-button>
        </template>
      </b-table>

      <b-modal v-model="showModal" :title="tituloModal" size="lg" hide-footer>
        <div v-if="detalhe">
          <b-row class="mb-2">
            <b-col cols="12">
              <h5>
                <b-badge variant="primary" class="p-2">{{ detalhe.codigo }}</b-badge>
                <span class="ml-2">{{ detalhe.nome }}</span>
                <b-badge variant="secondary" class="ml-2">{{ detalhe.segmento || '-' }}</b-badge>
              </h5>
            </b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col cols="6"><strong>Cotação:</strong> {{ formatarDinheiro(detalhe.cotacao_atual) }}</b-col>
            <b-col cols="6"><strong>P/VP:</strong> {{ detalhe.p_vp ?? '-' }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col cols="6"><strong>Dividend Yield:</strong> {{ formatarPercentual(detalhe.dividend_yield_percent) }}</b-col>
            <b-col cols="6"><strong>FFO Yield:</strong> {{ formatarPercentual(detalhe.ffo_yield_percent) }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col cols="6"><strong>Liquidez diária:</strong> {{ detalhe.liquidez_media_diaria ? detalhe.liquidez_media_diaria.toLocaleString('pt-BR') : '-' }}</b-col>
            <b-col cols="6"><strong>Valor Mercado:</strong> {{ formatarDinheiro(detalhe.valor_mercado) }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col cols="6"><strong>Preço/m²:</strong> {{ formatarDinheiro(detalhe.preco_m2) }}</b-col>
            <b-col cols="6"><strong>Aluguel/m²:</strong> {{ formatarDinheiro(detalhe.aluguel_m2) }}</b-col>
          </b-row>
          <b-row class="mb-2">
            <b-col cols="6"><strong>Cap rate:</strong> {{ formatarPercentual(detalhe.cap_rate_percent) }}</b-col>
            <b-col cols="6"><strong>Vacância média:</strong> {{ formatarPercentual(detalhe.vacancia_media_percent) }}</b-col>
          </b-row>

          <hr />

          <h6>Histórico de preços</h6>
          <b-row class="mb-2 text-center">
            <b-col>
              <b-button-group>
                <b-button v-for="op in opcoesFiltro" :key="op.value" :variant="filtroPreco === op.value ? 'primary' : 'outline-primary'" size="sm" @click="onFiltroPrecoChange(op.value)">{{ op.label }}</b-button>
              </b-button-group>
            </b-col>
          </b-row>
          <AtivoHistoricoChart v-if="historico.length" :historico="historico" />
          <div v-else class="text-muted small">Sem dados.</div>

          <h6 class="mt-3">Dividend Yield (%)</h6>
          <b-row class="mb-2 text-center">
            <b-col>
              <b-button-group>
                <b-button v-for="op in opcoesFiltro" :key="op.value" :variant="filtroDy === op.value ? 'primary' : 'outline-primary'" size="sm" @click="onFiltroDyChange(op.value)">{{ op.label }}</b-button>
              </b-button-group>
            </b-col>
          </b-row>
          <AtivoHistoricoChart v-if="dySeries.length" :historico="dySeries" />
          <div v-else class="text-muted small">Sem dados.</div>
        </div>
        <div v-else>
          <b-spinner small label="Carregando..." />
        </div>
      </b-modal>
    </b-card>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { BFormInput, BFormGroup, BFormSelect, BButton, BSpinner, BTable, BRow, BCol, BCard, BIcon, BModal, BBadge, BButtonGroup } from 'bootstrap-vue'
import AtivoHistoricoChart from './AtivoHistoricoChart.vue'

export default {
  components: { BFormInput, BFormGroup, BFormSelect, BButton, BSpinner, BTable, BRow, BCol, BCard, BIcon, BModal, BBadge, BButtonGroup, AtivoHistoricoChart },
  data() {
    return {
      fiis: [],
      segmentos: [],
      selectedSegmento: '',
      search: '',
      loading: false,
      fields: [
        { key: 'codigo', label: 'Código', sortable: true },
        { key: 'nome', label: 'Nome', sortable: true },
        { key: 'segmento', label: 'Segmento', sortable: true },
        { key: 'cotacao_atual', label: 'Cotação', sortable: true },
        { key: 'p_vp', label: 'P/VP', sortable: true },
        { key: 'dividend_yield_percent', label: 'DY (%)', sortable: true },
        { key: 'liquidez_media_diaria', label: 'Liquidez diária', sortable: true },
        { key: 'acoes', label: 'Ações' }
      ],
      showModal: false,
      detalhe: null,
      historico: [],
      rendimentos: [],
      dy: [],
      filtroPreco: '1y',
      filtroDy: '1y',
      opcoesFiltro: [
        { label: '1m', value: '1m' },
        { label: '6m', value: '6m' },
        { label: '1y', value: '1y' },
        { label: '5y', value: '5y' }
      ],
    }
  },
  computed: {
    ...mapGetters(['getToken', 'getDominio']),
    segmentoOptions() {
      return this.segmentos.map(s => ({ value: s, text: s }))
    },
    tituloModal() {
      if (!this.detalhe) return 'Detalhes'
      return `${this.detalhe.codigo} - ${this.detalhe.nome || ''}`
    },
    rendimentosSeries() {
      return this.rendimentos.map(r => ({ data: r.data, preco_fechamento: r.valor_rendimento }))
    },
    dySeries() {
      return this.dy.map(d => ({ data: d.data, preco_fechamento: Number(d.dy) * 100 }))
    }
  },
  methods: {
    async fetchFiis() {
      this.loading = true
      const params = []
      if (this.search) params.push(`search=${encodeURIComponent(this.search)}`)
      if (this.selectedSegmento) params.push(`segmento=${encodeURIComponent(this.selectedSegmento)}`)
      const qs = params.length ? `?${params.join('&')}` : ''
      try {
        const res = await fetch(`${this.getDominio}/api/ibovespa/fiis/${qs}`, {
          headers: { Authorization: `Token ${this.getToken}` }
        })
        if (!res.ok) throw new Error('Erro ao buscar FIIs')
        this.fiis = await res.json()
        this.segmentos = Array.from(new Set(this.fiis.map(f => f.segmento).filter(Boolean))).sort()
      } catch (e) { console.error(e) }
      finally { this.loading = false }
    },
    async abrirDetalhes(codigo) {
      this.showModal = true
      this.detalhe = null
      this.historico = []
      this.rendimentos = []
      this.dy = []
      try {
        const dRes = await fetch(`${this.getDominio}/api/ibovespa/fiis/${codigo}/`, { headers: { Authorization: `Token ${this.getToken}` }})
        if (dRes.ok) this.detalhe = await dRes.json()
        await Promise.all([
          this.carregarHistorico(codigo, this.filtroPreco),
          this.carregarDy(codigo, this.filtroDy),
        ])
      } catch (e) {
        console.error(e)
      }
    },
    async carregarHistorico(codigo, periodo) {
      let dataInicio = null
      const hoje = new Date()
      if (periodo === '1m') dataInicio = new Date(hoje.setMonth(hoje.getMonth() - 1))
      else if (periodo === '6m') dataInicio = new Date(hoje.setMonth(hoje.getMonth() - 6))
      else if (periodo === '1y') dataInicio = new Date(hoje.setFullYear(hoje.getFullYear() - 1))
      else if (periodo === '5y') dataInicio = new Date(hoje.setFullYear(hoje.getFullYear() - 5))

      const qs = dataInicio ? `?data_inicio=${dataInicio.toISOString().slice(0,10)}` : ''
      const hRes = await fetch(`${this.getDominio}/api/ibovespa/fiis/${codigo}/historico/${qs}`, { headers: { Authorization: `Token ${this.getToken}` }})
      this.historico = hRes.ok ? await hRes.json() : []
    },
    async carregarDy(codigo, periodo) {
      let dataInicio = null
      const hoje = new Date()
      if (periodo === '1m') dataInicio = new Date(hoje.setMonth(hoje.getMonth() - 1))
      else if (periodo === '6m') dataInicio = new Date(hoje.setMonth(hoje.getMonth() - 6))
      else if (periodo === '1y') dataInicio = new Date(hoje.setFullYear(hoje.getFullYear() - 1))
      else if (periodo === '5y') dataInicio = new Date(hoje.setFullYear(hoje.getFullYear() - 5))

      const qs = dataInicio ? `?data_inicio=${dataInicio.toISOString().slice(0,10)}` : ''
      const dyRes = await fetch(`${this.getDominio}/api/ibovespa/fiis/${codigo}/dy/${qs}`, { headers: { Authorization: `Token ${this.getToken}` }})
      this.dy = dyRes.ok ? await dyRes.json() : []
    },
    onFiltroPrecoChange(novo) {
      this.filtroPreco = novo
      if (this.detalhe) this.carregarHistorico(this.detalhe.codigo, novo)
    },
    onFiltroDyChange(novo) {
      this.filtroDy = novo
      if (this.detalhe) this.carregarDy(this.detalhe.codigo, novo)
    },
    formatarDinheiro(v) {
      if (v === null || v === undefined || isNaN(v)) return '-'
      return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
    },
    formatarPercentual(v) {
      if (v === null || v === undefined || isNaN(v)) return '-'
      return Number(v).toFixed(2) + '%'
    },
  },
  mounted() {
    this.fetchFiis()
  }
}
</script>

<style scoped>
.shadow-lg { box-shadow: 0 0.5rem 1rem rgba(44, 62, 80, 0.15) !important; }
.ml-3 { margin-left: 1rem; }
</style>

