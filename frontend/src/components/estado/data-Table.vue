<template>
  <div>
    <b-modal centered @ok="deletarItem" v-model="showModalDel" title="Apagar Item" no-stacking>
            <p>Deseja Ralmente deletar o Item <strong>{{apagarAlvo.info}}</strong>?</p>
    </b-modal>
            <b-row class="m-auto">
            <b-col cols="6">
            <b-form-group >
                <b-input-group>
                    <b-input-group-prepend is-text>
                        <b-icon :variant="lupaVariant" :animation="lupaAnima" icon='search'></b-icon>
                    </b-input-group-prepend>
                    <b-input v-model="filtro"  type='text'></b-input>
                    <b-button v-show="buscando" @click="limpaPesquisa" size='sm' variant='light'>
                        <b-icon icon='x-circle'></b-icon>
                    </b-button>
                </b-input-group>
            </b-form-group>
            </b-col>
            <b-col cols="6" class="text-right" v-if="temAdd">
                <b-button @click="adiciona()" size='md' variant='primary'>
                    <b-icon icon='plus-circle'></b-icon>
                </b-button>
            </b-col>
        </b-row>
   <b-table small responsive striped hover 
    :busy="esperando"
    :items=items 
    :fields=fields 
    :filter=filtro
    head-variant="dark">
    <template #cell(color)="row">
        <b-form-input  type="color" v-bind:value="row.item.color" disabled="true"></b-form-input>
    </template>
    <template #cell(action)="row">
        <b-button v-if="temEdit" type="button" size="sm" @click="edita(row.item.id)" class="mr-1">
         Editar 
        </b-button>
        <b-button v-if="temRemove" type="button" size="sm" @click="apaga(row.item.id)">
          Apagar
        </b-button>
    </template>

    </b-table>
</div>
</template>

<script lang="js">
export default {
  name: 'data-Table',
  data(){
    return{
        cor:"",
        showModalDel:false,
        apagarAlvo:{'id':0,'info':'nenhum'},
        filtro: '',
        falha: false,
        esperando: false,
    }
  },
  methods:{
    adiciona(){
        this.$emit("novo")
    },
    edita(id){
        this.$emit("editar",id)
    },
    apaga(id){
        this.apagarAlvo.id = id
        this.apagarAlvo.info = this.items.name
        this.showModalDel = true
    },
    deletarItem(){ 
      this.showModalDel = false
      this.$emit("apagar",this.apagarAlvo.id)
    },
    limpaPesquisa(){ this.filtro = '' },
  },
  computed:{
    temActions(){
        if (this.actions == [0,0,0]){
            return false
        }else{
            return true
        }
    },
    temAdd(){
        if(this.actions[0] > 0){return true}
        else{return false}
    },
    temRemove(){ 
        if(this.actions[2] > 0){return true}
        else{return false}},
    temEdit(){
        if(this.actions[1] > 0){return true}
        else{return false}
    },
    buscando(){
          if (this.filtro===null || this.filtro==''){
              return false
          }else{
              return this.filtro.length>0
          }
      },
      lupaAnima(){
          if(this.buscando){
              return "throb"
          }else{
              return ""
          }
      },
      lupaVariant(){
          if(this.buscando){
              return "success"
          }else{
              return "dark"
          }
        },
        erroIcone(){
            if (this.erro){
                return 'x-circle'
            }else{
                return 'arrow-clockwise'
            }
        },
        erroAnima(){
            if (this.erro){
                return ''
            }else{
                return 'spin'
            }
        }
  },
  props:{
    actions:{
        type: Array, 
        required:true,
        default() {
        return [0,0,0]
      }
    },
    items:{
        type: Array, 
        required:true,
        default() {
        return []
      }
    },
    fields:{
        type: Array, 
        required:false,
        default() {
        return []
      }
    },
  }
}
</script>
  