/* Local Eureka card. Uses only entities and capabilities supplied by HA. */
class EurekaRobotCard extends HTMLElement {
  constructor() { super(); this.attachShadow({mode:'open'}); this._busy=false; this._rooms=new Set(); this._repeats=1; }
  static getConfigElement() { return document.createElement('eureka-robot-card-editor'); }
  static getStubConfig(hass) {
    return {entity:Object.values(hass?.entities || {}).find(e=>e.entity_id.startsWith('vacuum.')&&e.platform==='eureka_robot')?.entity_id || ''};
  }
  setConfig(config) {
    if (config.entity && !config.entity.startsWith('vacuum.')) throw new Error('Select a vacuum entity');
    if (this._config?.entity!==config.entity) this._rooms.clear();
    this._config={...config}; this.render();
  }
  // HA pushes hass on every state change in the house; rebuilding the card each time
  // destroys an open <select>. Re-render only when this robot's entities change,
  // and wait while the user has a select open.
  set hass(hass) {
    this._hass=hass;
    const sig=this._signature();
    if (sig===this._sig) return;
    if (this._picking) { this._stale=true; return; }
    this.render();
  }
  _signature() {
    const h=this._hass, id=this._config?.entity;
    if (!h || !id) return '';
    if (h.entities!==this._entitiesRef || id!==this._idsFor) {
      const device=h.entities?.[id]?.device_id;
      this._ids=[id,...Object.values(h.entities || {}).filter(e=>device && e.device_id===device && e.entity_id!==id).map(e=>e.entity_id)];
      this._entitiesRef=h.entities;this._idsFor=id;
    }
    return [h.locale?.language || h.language,...this._ids.map(e=>`${e}:${h.states[e]?.last_updated || ''}`)].join('|');
  }
  _pickDone() { this._picking=false; if (this._stale) { this._stale=false; this.render(); } }
  getCardSize() { return 8; }
  render() {
    if (!this._hass || !this._config) return;
    this._sig=this._signature();
    const h=this._hass, root=this.shadowRoot;
    const es=(h.locale?.language || h.language || '').startsWith('es');
    const w=es ? {offline:'Sin conexión',start:'Iniciar',pause:'Pausar',stop:'Detener',dock:'Volver a base',wash:'Lavar mopas',empty:'Vaciar polvo',dry:'Secar mopas',stopDry:'Detener secado',basin:'Limpiar bandeja',unknown:'Desconocido',mode:'Modo de limpieza',water:'Agua',fan:'Succión',rooms:'Habitaciones',selected:'Limpiar selección',repeats:'Repeticiones',area:'Área',time:'Tiempo',pick:'Selecciona una aspiradora Eureka en el editor.',room:'Habitación',checkWater:'Revisar agua'} :
      {offline:'Offline',start:'Start',pause:'Pause',stop:'Stop',dock:'Dock',wash:'Wash mops',empty:'Empty dust',dry:'Dry mops',stopDry:'Stop drying',basin:'Clean basin',unknown:'Unknown',mode:'Cleaning mode',water:'Water',fan:'Suction',rooms:'Rooms',selected:'Clean selected',repeats:'Repeats',area:'Area',time:'Time',pick:'Select an Eureka vacuum in the card editor.',room:'Room',checkWater:'Check water'};
    if (!this._config.entity) { root.innerHTML='<ha-card style="display:block;padding:20px"></ha-card>'; root.firstChild.textContent=w.pick; return; }
    const s=h.states[this._config.entity], offline=!s || ['unavailable','unknown'].includes(s.state), features=s?.attributes.supported_features || 0;
    const labels=es ? {docked:'En la base',cleaning:'Limpiando',paused:'En pausa',returning:'Regresando',idle:'En espera',error:'Error'} :
      {docked:'Docked',cleaning:'Cleaning',paused:'Paused',returning:'Returning',idle:'Idle',error:'Error'};
    const device=h.entities?.[this._config.entity]?.device_id;
    const related=Object.values(h.entities || {}).filter(e=>device && e.device_id===device && e.platform==='eureka_robot');
    const find=role=>related.find(e=>h.states[e.entity_id]?.attributes.eureka_role===role)?.entity_id;
    const entity=role=>h.states[find(role)];
    const known=state=>state && !['unknown','unavailable'].includes(state.state);
    root.innerHTML=`<style>
      :host{display:block}*{box-sizing:border-box}ha-card{display:block;padding:20px;background:var(--ha-card-background,var(--card-background-color));color:var(--primary-text-color);overflow:hidden}
      header{display:flex;gap:14px;align-items:center}header>div{min-width:0}.icon{width:48px;height:48px;flex-shrink:0;color:var(--primary-color)}
      h2{font:600 18px var(--paper-font-body1_-_font-family,sans-serif);margin:0;overflow-wrap:anywhere}h3{font:600 14px sans-serif;margin:0 0 10px}
      p{margin:5px 0;color:var(--secondary-text-color)}.actions,.station-actions,.room-chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
      button,select{min-height:44px;padding:10px 12px;border:1px solid var(--divider-color);border-radius:12px;background:var(--secondary-background-color);color:var(--primary-text-color);font:inherit}
      button{flex:1;cursor:pointer}button.primary,button[aria-pressed=true]{background:var(--primary-color);color:var(--text-primary-color,white);border-color:transparent}
      button:disabled,select:disabled{opacity:.45;cursor:default}button:focus-visible,select:focus-visible{outline:2px solid var(--primary-color);outline-offset:3px}
      .section{margin-top:18px;padding-top:16px;border-top:1px solid var(--divider-color)}.settings,.metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
      label{display:flex;flex-direction:column;gap:6px;min-width:0;font-size:13px;color:var(--secondary-text-color)}select{width:100%;min-width:0;font-size:14px}.settings label:first-child{grid-column:1/-1}
      .metrics{margin-top:16px;font-size:13px}.metric strong{display:block;font-size:18px;color:var(--primary-text-color)}.error{color:var(--error-color);overflow-wrap:anywhere}.alert{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:16px;padding:10px 12px;border-radius:12px;background:rgba(var(--rgb-error-color,219,68,55),.12);color:var(--error-color)}.alert span{flex:1 1 160px;font-weight:600;overflow-wrap:anywhere}.alert button{flex:0 0 auto}[hidden]{display:none!important}
      @media(max-width:340px){ha-card{padding:14px}button{padding:10px}.actions,.station-actions{gap:6px}}
      </style><ha-card><header><svg class="icon" viewBox="0 0 48 48" fill="none" aria-hidden="true"><circle cx="24" cy="25" r="19" stroke="currentColor" stroke-width="2"/><rect x="18" y="10" width="12" height="7" rx="3" stroke="currentColor" stroke-width="2"/><path d="M13 32h22M20 23h8" stroke="currentColor" stroke-width="2"/></svg><div><h2></h2><p class="state" role="status"></p><p class="battery"></p></div></header><div class="alert" hidden><span></span></div><div class="actions"></div><div class="metrics"></div><div class="settings section" hidden></div><div class="station section" hidden><p></p><div class="station-actions"></div></div><div class="rooms section" hidden><h3></h3><div class="room-chips"></div><div class="room-footer actions"></div></div><p class="error" role="alert" hidden></p></ha-card>`;
    root.querySelector('h2').textContent=s?.attributes.friendly_name || 'Eureka';
    root.querySelector('.state').textContent=offline ? w.offline : labels[s.state] || w.unknown;
    const battery=entity('battery'); root.querySelector('.battery').textContent=known(battery) ? `${battery.state}%` : '';
    const addButton=(parent,label,handler,enabled=true,primary=false)=>{
      const b=document.createElement('button');b.textContent=label;b.disabled=offline || this._busy || !enabled;
      b.className=primary?'primary':'';b.onclick=handler;parent.append(b);return b;
    };
    const faults=['robot_fault','station_fault'].map(entity).filter(e=>known(e) && e.state!=='none');
    const alert=root.querySelector('.alert'), shortage=entity('water_shortage')?.state==='on';
    if (faults.length || shortage) {
      alert.hidden=false;alert.setAttribute('role','alert');
      alert.querySelector('span').textContent=faults.map(e=>h.formatEntityState?.(e) ?? e.state).join(' · ') || (h.formatEntityState?.(entity('water_shortage')) ?? '');
      const check=find('check_water');
      if (shortage && check) addButton(alert,w.checkWater,()=>this.call('button','press',check),s?.state==='docked' && h.states[check]?.state!=='unavailable',true);
    }
    const actions=root.querySelector('.actions');
    if (s?.state==='cleaning' && (features&4)) addButton(actions,w.pause,()=>this.call('vacuum','pause',this._config.entity),true,true);
    else if (features&8192) addButton(actions,w.start,()=>this.call('vacuum','start',this._config.entity),true,true);
    if (features&8) addButton(actions,w.stop,()=>this.call('vacuum','stop',this._config.entity));
    if (features&16) addButton(actions,w.dock,()=>this.call('vacuum','return_to_base',this._config.entity));
    for (const [role,label,unit] of [['cleaned_area',w.area,'m²'],['clean_time',w.time,'min']]) {
      const value=entity(role);if (!known(value)) continue;
      const metric=document.createElement('div');metric.className='metric';metric.textContent=label;
      const strong=document.createElement('strong');strong.textContent=`${value.state} ${unit}`;metric.append(strong);root.querySelector('.metrics').append(metric);
    }
    const settings=root.querySelector('.settings');
    const optionLabels=es ? {vacuum_and_mop:'Aspirar y fregar',vacuum:'Aspirar',mop:'Fregar',vacuum_then_mop:'Aspirar y luego fregar',off:'Apagado',soft:'Silenciosa',normal:'Normal',high:'Alta',low:'Baja',max:'Máxima'} :
      {vacuum_and_mop:'Vacuum and mop',vacuum:'Vacuum',mop:'Mop',vacuum_then_mop:'Vacuum then mop',off:'Off',soft:'Quiet',normal:'Normal',high:'High',low:'Low',max:'Max'};
    const addSelect=(label,options,current,handler,enabled=true)=>{
      settings.hidden=false;const field=document.createElement('label');field.textContent=label;
      const select=document.createElement('select');select.setAttribute('aria-label',label);select.disabled=offline || this._busy || !enabled;
      if (!options.includes(current)) { const option=document.createElement('option');option.value='';option.textContent='—';option.disabled=true;select.append(option); }
      for (const value of options) { const option=document.createElement('option');option.value=value;option.textContent=optionLabels[value] || value;select.append(option); }
      select.value=current || '';select.onfocus=()=>this._picking=true;select.onblur=()=>this._pickDone();select.onchange=()=>{this._picking=false;this._stale=false;handler(select.value);};field.append(select);settings.append(field);
    };
    for (const [role,label] of [['clean_mode',w.mode],['water_level',w.water]]) {
      const id=find(role), e=h.states[id];
      if (e?.attributes.options?.length) addSelect(label,e.attributes.options,e.state,value=>this.call('select','select_option',id,{option:value}),known(e));
    }
    if ((features&32) && s?.attributes.fan_speed_list?.length) addSelect(w.fan,s.attributes.fan_speed_list,s.attributes.fan_speed,value=>this.call('vacuum','set_fan_speed',this._config.entity,{fan_speed:value}));
    const station=root.querySelector('.station');
    const stationLabels=es ? {idle:'En espera',charging:'Cargando',filling_water:'Llenando agua',washing:'Lavando',drying:'Secando',air_drying:'Ventilando',error:'Error',charged:'Cargado',sleeping:'En reposo',self_cleaning:'Limpiando bandeja',emptying:'Vaciando polvo',cutting_hair:'Cortando pelo',waiting_to_charge:'Esperando carga',draining:'Vaciando agua'} : {};
    const st=entity('station_status');station.querySelector('p').textContent=known(st) ? stationLabels[st.state] || (h.formatEntityState?.(st) ?? st.state) : '';
    for (const [role,label] of [['wash_mops',w.wash],['empty_dust',w.empty],['dry_mops',w.dry],['stop_drying',w.stopDry],['clean_station',w.basin]]) {
      const id=find(role);if (!id) continue;station.hidden=false;
      addButton(station.querySelector('.station-actions'),label,()=>this.call('button','press',id),s?.state==='docked' && h.states[id]?.state!=='unavailable');
    }
    const rooms=s?.attributes.rooms;
    if (rooms && Object.keys(rooms).length) {
      const section=root.querySelector('.rooms');section.hidden=false;section.querySelector('h3').textContent=w.rooms;
      for (const id of [...this._rooms]) if (!(id in rooms)) this._rooms.delete(id);
      for (const [id,name] of Object.entries(rooms)) {
        const label=name===`Room ${id}` ? `${w.room} ${id}` : name;
        const b=addButton(section.querySelector('.room-chips'),label,()=>{this._rooms.has(id)?this._rooms.delete(id):this._rooms.add(id);this.render();});
        b.setAttribute('aria-pressed',String(this._rooms.has(id)));
        if (this._rooms.size>=10 && !this._rooms.has(id)) b.disabled=true;
      }
      const footer=section.querySelector('.room-footer');
      const repeats=document.createElement('select');repeats.setAttribute('aria-label',w.repeats);repeats.style.width='auto';
      for (const n of [1,2,3]) { const o=document.createElement('option');o.value=n;o.textContent=`×${n}`;repeats.append(o); }
      repeats.value=this._repeats;repeats.disabled=offline || this._busy;repeats.onfocus=()=>this._picking=true;repeats.onblur=()=>this._pickDone();repeats.onchange=()=>{this._repeats=Number(repeats.value);this._picking=false;};footer.append(repeats);
      addButton(footer,w.selected,()=>this.call('eureka_robot','clean_rooms',this._config.entity,{rooms:[...this._rooms].map(Number),repeats:this._repeats}),this._rooms.size>0,true);
    }
    if (this._error) { const error=root.querySelector('.error');error.hidden=false;error.textContent=this._error; }
  }
  async call(domain,service,entity_id,data={}) {
    this._busy=true;this._error='';this.render();
    try { await this._hass.callService(domain,service,{entity_id,...data}); if (service==='clean_rooms') this._rooms.clear(); }
    catch (err) { this._error=err.message || String(err); }
    finally { this._busy=false;this.render(); }
  }
}
class EurekaRobotCardEditor extends HTMLElement {
  setConfig(config) { this._config={...config};this.render(); }
  set hass(hass) { this._hass=hass;this.render(); }
  render() {
    if (!this._hass || !this._config) return;
    if (!this._form) {
      this._form=document.createElement('ha-form');this._form.schema=[{name:'entity',selector:{entity:{domain:'vacuum',integration:'eureka_robot'}}}];
      this._form.computeLabel=()=>'Eureka vacuum';
      this._form.addEventListener('value-changed',e=>{this._config={...this._config,...e.detail.value};this.dispatchEvent(new CustomEvent('config-changed',{detail:{config:this._config},bubbles:true,composed:true}));});this.append(this._form);
    }
    this._form.hass=this._hass;this._form.data=this._config;
  }
}
if (!customElements.get('eureka-robot-card')) customElements.define('eureka-robot-card',EurekaRobotCard);
if (!customElements.get('eureka-robot-card-editor')) customElements.define('eureka-robot-card-editor',EurekaRobotCardEditor);
window.customCards=window.customCards || [];
if (!window.customCards.some(c=>c.type==='eureka-robot-card')) window.customCards.push({type:'eureka-robot-card',name:'Eureka Robot',description:'Local Eureka robot controls',preview:true});
