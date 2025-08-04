<template>
    <div>
      <!-- aqui o modal que vai mostrar erros na tela: -->
      <b-modal v-model="modalVisible" centered ok-only title="Erro" no-stacking>
        <div class="d-flex flex-column align-items-center">
          <b-alert show variant="danger" class="mt-3">
          <b-icon icon="exclamation-circle-fill"></b-icon>
            {{ erroMsg }}
          </b-alert>
        </div>
      </b-modal>

      <b-modal v-model="modalAddVisible" centered ok-only 
        title="Cadastrar"
        @close="getDadosOS"
        @ok="getDadosOS"
      >
        <div class="d-flex flex-column align-items-center">
          <dataAdd></dataAdd>
        </div>
      </b-modal>

      <b-modal v-model="modalEditVisible" centered ok-only 
        title="Cadastrar"
        @close="getDadosOS"
        @ok="getDadosOS"
      >
        <div class="d-flex flex-column align-items-center">
          <dataEdit @editado="editado" :id="editIndex" ></dataEdit>
        </div>
      </b-modal>
      <div class="m-auto p-5">
        <h3>Gestão de Estado</h3>
      </div>
      <b-overlay rounded="sm" :show="esperando">
        <dataTable :actions="act" :items="data" :fields="fields"
          @novo="chamaAdd"
          @editar="chamaEdit"
          @apagar = "chamaDel"
        ></dataTable> 
      </b-overlay>
    </div>
</template>

<script>
import { mapGetters } from 'vuex'
import dataTable from '@/components/estado/data-Table.vue';
import dataAdd from '@/components/estado/data-Add.vue'
import dataEdit from '@/components/estado/data-Edit.vue';
export default {
  components:{
    dataTable,
    dataAdd,
    dataEdit
  },
  data(){    
    return {
      modalVisible:false,
      modalAddVisible:false,
      modalEditVisible:false,
      editIndex:0,
      erroMsg:'',
      act: [1,1,1], //novo,edit,apaga
      esperando: false,
      falha: false,
      data:[], // data precisa ter a key action se não não libera ferramentas
      fields:[
        {key:'id'},
        {key:'name',label:'Estado',sortable:true},
        {key:'color',label:'cor',sortable:true},
        {key:'action',label:'ação'}
      ]
    }
  },
  created(){
    this.getDadosOS()
  },
  computed:{
    ...mapGetters(['getDominio','getToken'])
  },
  methods:{
    informe(valor){
      alert(valor)
    },
    chamaAdd(){
      this.modalAddVisible = true
    },
    chamaEdit(valor){
      this.modalEditVisible = true
      this.editIndex=valor
    },
    chamaDel(valor){
      this.deleteOS(valor)
    },
    editado(){
      this.$bvToast.toast('Editado!!!', {
            title: "Bem Sucedido",
            variant: "success",
            solid: true
          })
      this.modalEditVisible=false
      this.getDadosOS()
    },
    async getDadosOS(){
      try{
        this.esperando = true
          const response = await fetch(`${this.getDominio}/api/os/estado/`,{
          headers:{
            'Authorization': `Token ${this.getToken}`
          }
        })
        if(response.ok){
          const data = await response.json()
          this.esperando = false
          this.data = data
          this.falha = false
        }else{
          switch(response.status){
            case 401:
              throw new Error('Não Autorizado');
            case 404:
              throw new Error('Não Encontrado');
            default:
              throw new Error('Falha interna no Servidor');
          }
        }
      }catch(error){
        this.modalVisible = true
        this.erroMsg = error
        this.falha = true
        this.esperando = false
      }
    },
   
    async deleteOS(id){
      try{
        this.esperando = true
          const response = await fetch(`${this.getDominio}/api/os/estado/${id}/`,{
            method:"DELETE",
          headers:{
            'Authorization': `Token ${this.getToken}`,
          }
        })
        if(response.ok){
          this.esperando = false
          this.falha = false
          this.getDadosOS()
          this.$bvToast.toast('Apagado Com Sucesso', {
            title: "Bem Sucedido",
            variant: "success",
            solid: true
          })
          
        }else{
          switch(response.status){
            case 401:
              throw new Error('Não Autorizado');
            case 404:
              throw new Error('Não Encontrado');
            default:
              throw new Error('Falha interna no Servidor');
          }
        }
      }catch(error){
        this.modalVisible = true
        this.erroMsg = error
        this.falha = true
        this.esperando = false
      }
    }
  }
}
</script>
  
 