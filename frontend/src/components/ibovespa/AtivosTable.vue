<template>
  <div>
    <b-card class="shadow-lg p-4">
      <b-form-group label="Filtros" label-for="search-input" class="mb-3">
        <b-form-input
          id="search-input"
          v-model="search"
          placeholder="Buscar por código, nome, setor..."
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
        <b-col cols="4" class="d-flex align-items-center justify-content-end">
          <b-button variant="primary" @click="fetchAtivos" :disabled="loading">
            <b-icon icon="search" class="mr-1" /> Buscar
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
        class="mb-3 sticky-header"
        :empty-text="'Nenhum ativo encontrado.'"
      >
        <template #cell(preco_atual)="data">
          {{ formatarDinheiro(data.item.preco_atual) }}
        </template>
        <template #cell(variacao)="data">
          <span :class="{'text-success': data.item.variacao > 0, 'text-danger': data.item.variacao < 0}">
            {{ formatarPercentual(data.item.variacao) }}
          </span>
        </template>
        <template #cell(dividendo_percentual)="data">
          {{ formatarPercentual(data.item.dividendo_percentual) }}
        </template>
        <template #cell(acoes)="data">
          <b-button size="sm" variant="success" @click="adicionarAcao(data.item)" v-b-tooltip.hover title="Adicionar ativo à sua carteira">
            <b-icon icon="plus-circle" /> Adicionar
          </b-button>
          <b-button size="sm" variant="info" class="ml-2" @click="abrirModalDetalhes(data.item)" v-b-tooltip.hover title="Ver detalhes do ativo">
            <b-icon icon="info-circle" />
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
      <b-toast v-model="showToast" variant="success" auto-hide-delay="2000" solid>
        Ativo adicionado com sucesso!
      </b-toast>

      <b-modal v-model="showModal" title="Detalhes do Ativo" @hide="fecharModalDetalhes" size="lg" hide-footer>
        <div v-if="ativoDetalhado">
          <b-container fluid>
            <!-- Filtros do gráfico -->
            <b-row class="mb-2">
              <b-col cols="12" class="text-center">
                <b-button-group>
                  <b-button
                    v-for="opcao in opcoesFiltro"
                    :key="opcao.value"
                    :variant="filtroHistorico === opcao.value ? 'primary' : 'outline-primary'"
                    size="sm"
                    @click="onFiltroHistoricoChange(opcao.value)"
                  >
                    {{ opcao.label }}
                  </b-button>
                </b-button-group>
              </b-col>
            </b-row>
            <!-- Gráfico de histórico -->
            <b-row class="mb-4">
              <b-col cols="12">
                <h5 class="mb-2">Histórico de Preço de Fechamento</h5>
                <AtivoHistoricoChart v-if="historicoAtivo.length" :historico="historicoAtivo" />
                <div v-else class="text-muted small">Sem dados de histórico para este ativo.</div>
              </b-col>
            </b-row>
            <!-- Detalhes do ativo -->
            <b-row class="mb-2">
              <b-col cols="12" class="text-center mb-2">
                <h4>
                  <b-badge variant="primary" class="p-2">{{ ativoDetalhado.codigo }}</b-badge>
                  <span class="ml-2">{{ ativoDetalhado.nome }}</span>
                </h4>
                <div>
                  <b-badge variant="info" class="mr-2">{{ ativoDetalhado.setor && ativoDetalhado.setor.nome ? ativoDetalhado.setor.nome : ativoDetalhado.setor }}</b-badge>
                  <b-badge variant="secondary">{{ ativoDetalhado.segmento && ativoDetalhado.segmento.nome ? ativoDetalhado.segmento.nome : ativoDetalhado.segmento }}</b-badge>
                </div>
              </b-col>
            </b-row>
            <b-row class="mb-3">
              <b-col cols="6"><strong>Preço Atual:</strong> <span class="text-success">{{ formatarDinheiro(ativoDetalhado.preco_atual) }}</span></b-col>
              <b-col cols="6"><strong>Variação:</strong> <span :class="{'text-success': ativoDetalhado.variacao > 0, 'text-danger': ativoDetalhado.variacao < 0}">{{ formatarPercentual(ativoDetalhado.variacao) }}</span></b-col>
            </b-row>
            <b-row class="mb-3">
              <b-col cols="12"><strong>Descrição:</strong> <span>{{ ativoDetalhado.descricao || '-' }}</span></b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Tipo:</strong> {{ ativoDetalhado.tipo }}</b-col>
              <b-col cols="6"><strong>Funcionários:</strong> {{ ativoDetalhado.funcionarios || '-' }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Fechamento Anterior:</strong> {{ formatarDinheiro(ativoDetalhado.fechamento_anterior) }}</b-col>
              <b-col cols="6"><strong>Volume:</strong> {{ ativoDetalhado.volume ? ativoDetalhado.volume.toLocaleString('pt-BR') : '-' }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Alta do Dia:</strong> {{ formatarDinheiro(ativoDetalhado.alta_do_dia) }}</b-col>
              <b-col cols="6"><strong>Baixa do Dia:</strong> {{ formatarDinheiro(ativoDetalhado.baixa_do_dia) }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Menor Preço 52s:</strong> {{ formatarDinheiro(ativoDetalhado.menor_preco_52s) }}</b-col>
              <b-col cols="6"><strong>Maior Preço 52s:</strong> {{ formatarDinheiro(ativoDetalhado.maior_preco_52s) }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Dividendo Valor:</strong> {{ formatarDinheiro(ativoDetalhado.dividendo_valor) }}</b-col>
              <b-col cols="6"><strong>Dividendo %:</strong> {{ formatarPercentual(ativoDetalhado.dividendo_percentual) }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Lucro/Dividendo %:</strong> {{ formatarPercentual(ativoDetalhado.percentual_lucro_dividendo) }}</b-col>
              <b-col cols="6"><strong>Média Dividendo 5 anos:</strong> {{ formatarPercentual(ativoDetalhado.media_dividendo_5anos) }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Risco Mercado (Beta):</strong> {{ ativoDetalhado.risco_mercado_beta }}</b-col>
              <b-col cols="6"><strong>Dívida/Patrimônio:</strong> {{ ativoDetalhado.divida_sobre_patrimonio }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Dívida Total:</strong> {{ ativoDetalhado.divida_total }}</b-col>
              <b-col cols="6"><strong>Preço Alvo Alta:</strong> {{ formatarDinheiro(ativoDetalhado.preco_alvo_alta) }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Preço Alvo Média:</strong> {{ formatarDinheiro(ativoDetalhado.preco_alvo_media) }}</b-col>
              <b-col cols="6"><strong>Preço Alvo Baixa:</strong> {{ formatarDinheiro(ativoDetalhado.preco_alvo_baixa) }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="6"><strong>Preço Alvo Ideal:</strong> {{ formatarDinheiro(ativoDetalhado.preco_alvo_ideal) }}</b-col>
              <b-col cols="6"><strong>Data Atualização:</strong> {{ ativoDetalhado.data_atualizacao ? new Date(ativoDetalhado.data_atualizacao).toLocaleString('pt-BR') : '-' }}</b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col cols="12"><strong>Riscos:</strong>
                <ul class="mb-0">
                  <li><strong>Auditoria:</strong> {{ ativoDetalhado.risco_auditoria || '-' }}</li>
                  <li><strong>Administrativo:</strong> {{ ativoDetalhado.risco_administrativo || '-' }}</li>
                  <li><strong>Executivos:</strong> {{ ativoDetalhado.risco_executivos || '-' }}</li>
                  <li><strong>Acionista:</strong> {{ ativoDetalhado.risco_acionista || '-' }}</li>
                  <li><strong>Médio:</strong> {{ ativoDetalhado.risco_medio || '-' }}</li>
                </ul>
              </b-col>
            </b-row>
          </b-container>
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
import { BFormInput, BFormGroup, BFormSelect, BButton, BSpinner, BTable, BPagination, BRow, BCol, BCard, BIcon, BToast, VBTooltip, BContainer, BBadge } from 'bootstrap-vue'
import AtivoHistoricoChart from './AtivoHistoricoChart.vue'

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
    BCol,
    BCard,
    BIcon,
    BToast,
    BContainer,
    BBadge,
    AtivoHistoricoChart
  },
  directives: { 'b-tooltip': VBTooltip },
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
      showToast: false,
      showModal: false,
      ativoDetalhado: null,
      historicoAtivo: [],
      filtroHistorico: '1y',
      opcoesFiltro: [
        { label: '1m', value: '1m' },
        { label: '6m', value: '6m' },
        { label: '1y', value: '1y' },
        { label: '5y', value: '5y' }
      ],
      fields: [
        { key: 'codigo', label: 'Código', sortable: true },
        { key: 'nome', label: 'Nome', sortable: true },
        { key: 'setor', label: 'Setor', sortable: true },
        { key: 'segmento', label: 'Segmento', sortable: true },
        { key: 'preco_atual', label: 'Preço Atual', sortable: true },
        { key: 'variacao', label: 'Variação (%)', sortable: true },
        { key: 'dividendo_percentual', label: 'Dividendo (%)', sortable: true },
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
    },
    chavesDetalhadas() {
      if (!this.ativoDetalhado) return {}
      // Exclui os campos já exibidos acima
      const ignorar = ['codigo','nome','setor','segmento','preco_atual','variacao']
      return Object.keys(this.ativoDetalhado)
        .filter(chave => !ignorar.includes(chave))
        .reduce((obj, chave) => {
          obj[chave] = this.ativoDetalhado[chave]
          return obj
        }, {})
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
    },
    adicionarAcao(item) {
      this.$emit('adicionar-acao', item)
      this.showToast = true
    },
    abrirModalDetalhes(ativo) {
      this.ativoDetalhado = null;
      this.historicoAtivo = [];
      this.filtroHistorico = '1y';
      this.showModal = true;
      this.carregarDetalhesAtivo(ativo.codigo);
      this.carregarHistoricoAtivo(ativo.codigo, this.filtroHistorico);
    },
    async carregarDetalhesAtivo(codigo) {
      try {
        const res = await fetch(`${this.getDominio}/api/ibovespa/ativos/${codigo}/`, {
          headers: { Authorization: `Token ${this.getToken}` }
        });
        if (!res.ok) throw new Error('Erro ao buscar detalhes do ativo');
        this.ativoDetalhado = await res.json();
      } catch (err) {
        this.ativoDetalhado = null;
        this.$bvToast.toast('Erro ao carregar detalhes do ativo.', {
          title: 'Erro',
          variant: 'danger',
          solid: true
        });
      }
    },
    async carregarHistoricoAtivo(codigo, periodo = '1y') {
      try {
        // Calcula a data inicial baseada no filtro
        let dataInicio = null;
        const hoje = new Date();
        if (periodo === '1m') {
          dataInicio = new Date(hoje.setMonth(hoje.getMonth() - 1));
        } else if (periodo === '6m') {
          dataInicio = new Date(hoje.setMonth(hoje.getMonth() - 6));
        } else if (periodo === '1y') {
          dataInicio = new Date(hoje.setFullYear(hoje.getFullYear() - 1));
        } else if (periodo === '5y') {
          dataInicio = new Date(hoje.setFullYear(hoje.getFullYear() - 5));
        }
        let url = `${this.getDominio}/api/ibovespa/ativos/${codigo}/historico/`;
        if (dataInicio) {
          const dataStr = dataInicio.toISOString().slice(0, 10);
          url += `?data_inicio=${dataStr}`;
        }
        const res = await fetch(url, {
          headers: { Authorization: `Token ${this.getToken}` }
        });
        if (!res.ok) throw new Error('Erro ao buscar histórico do ativo');
        this.historicoAtivo = await res.json();
      } catch (err) {
        this.historicoAtivo = [];
        this.$bvToast.toast('Erro ao carregar histórico do ativo.', {
          title: 'Erro',
          variant: 'danger',
          solid: true
        });
      }
    },
    onFiltroHistoricoChange(novoFiltro) {
      this.filtroHistorico = novoFiltro;
      if (this.ativoDetalhado && this.ativoDetalhado.codigo) {
        this.carregarHistoricoAtivo(this.ativoDetalhado.codigo, novoFiltro);
      }
    },
    fecharModalDetalhes() {
      this.showModal = false;
      this.ativoDetalhado = null;
    },
    formatarDinheiro(valor) {
      if (valor === null || valor === undefined || isNaN(valor)) return '-';
      return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    },
    formatarPercentual(valor) {
      if (valor === null || valor === undefined || isNaN(valor)) return '-';
      return Number(valor).toFixed(3) + '%';
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
.shadow-lg {
  box-shadow: 0 0.5rem 1rem rgba(44, 62, 80, 0.15) !important;
}
.sticky-header >>> .table thead th {
  position: sticky;
  top: 0;
  background: #f8f9fa;
  z-index: 2;
}
.text-success {
  color: #28a745 !important;
}
.text-danger {
  color: #dc3545 !important;
}
.b-modal .modal-content {
  border-radius: 1rem;
  box-shadow: 0 0.5rem 2rem rgba(44, 62, 80, 0.15) !important;
}
.b-badge {
  font-size: 1.1em;
}
.b-modal h4 {
  font-weight: 600;
  color: #2c3e50;
}
.b-modal ul {
  padding-left: 1.2em;
}
</style>