from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivy.properties import NumericProperty,DictProperty
from kivy.utils import platform
import crud
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.screen import MDScreen
from widgets.widgets import Cards,Buttons,ContentNvoPrestamo,ContentGastos
from kivymd.utils import asynckivy as ak
from datetime import date
from kivy.clock import Clock
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
import os

Builder.load_file(os.path.join("screens","screenFondo","screenFondo.kv"))


class ScreenFondo(MDScreen):
    built=False

    ahorro=NumericProperty(0)
    prestamos_list=DictProperty({"tarjeta":0})
    who = 'luis' if not (platform in ['macosx','ios']) else 'joss'
    dialogNvoPrestamo=None
    dialogRegistro=None

    def on_enter(self):
        if self.built==False:
            Clock.schedule_once(lambda x:self.fondo_init_consulta(),0)
            self.built=True

    def fondo_init_consulta(self):
        async def fondo_init_consulta():
            # construyendo la pagina de ahorros
            tarjeta = crud.get(f'fondo/{self.who}/{"tarjeta"}')
            print(tarjeta)
            self.addItemTarjeta(tarjeta)
            prestamos = crud.get(f'fondo/{self.who}/prestamos')
            self.prestamos_list['tarjeta'] = eval(tarjeta)
            if prestamos is None:return None
            for key,value in prestamos.items():
                saldo = 0
                for j in ('ingresos', 'egresos'):
                    op = crud.get(f'fondo/{self.who}/prestamos/{key}/{j}')
                    print(op)
                    if op is None:
                        pass
                    else:
                        for _key,_value in op.items():
                            if j == 'ingresos':
                                saldo += eval(_value['monto'])
                            else: saldo -= eval(_value['monto'])
                await ak.sleep(0)
                self.addItem(key, saldo)
        ak.start(fondo_init_consulta())
        
    def addItemTarjeta(self,data):
        async def addItemTarjeta():
            card = Cards()
            content = Buttons()
            card.add_widget(
                MDExpansionPanel(
                        content=content,
                            panel_cls=MDExpansionPanelTwoLine(text='En tarjeta del banco', secondary_text='En esta cuenta: '+"${:,.2f}".format(self.prestamos_list['tarjeta'])),
                    )
            )
            self.ids.layout_fondo.add_widget(card)
        self.prestamos_list['tarjeta'] = float(data)
        self.ahorro += abs(float(data))
        ak.start(addItemTarjeta())

    def addItem(self,nombre,saldo):
        async def addItem():
            card = Cards()
            content = Buttons()
            card.add_widget(
                MDExpansionPanel(
                    content=content,
                    panel_cls=MDExpansionPanelTwoLine(text='Prestamo '+nombre, secondary_text='En esta cuenta: '+"${:,.2f}".format(self.prestamos_list[nombre]))
                )
            )
            self.ids.layout_fondo.add_widget(card)
        self.prestamos_list[nombre] = saldo
        self.ahorro += abs(saldo)
        ak.start(addItem())
    
    def nuevo_prestamo(self):
        def clean_fields():
            self.dialogNvoPrestamo.content_cls.ids.descripcion.text = ''

        def registrar(object):
            nombre = self.dialogNvoPrestamo.content_cls.ids.descripcion.text
            try:
                crud.update(f'fondo/{self.who}/prestamos',{nombre:""})
            except:
                Snackbar(MDLabel(text="¡Ocurrió un error!")).open()
                return None
            self.addItem(nombre,0)
            self.dialogNvoPrestamo.dismiss()
            clean_fields()

        def cancelar(object):
            clean_fields()
            self.dialogNvoPrestamo.dismiss()

        if self.dialogNvoPrestamo is None:
            self.dialogNvoPrestamo = MDDialog(
            title='Nuevo préstamo',
            type='custom',
            content_cls=ContentNvoPrestamo(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=registrar)]
        )
        self.dialogNvoPrestamo.open()

    def validacion(self, field, text):
        if field == 'monto':
            if '.' in text:
                try:
                    float(text)
                    return True
                except ValueError:
                    return False
            else:
                return text.isnumeric()
        elif field == 'descripcion':
            if not text == '':
                return True
            else:
                False

    def refresh(self):
        async def refresh():
            ahorrau = 0
            for i in self.ids.layout_fondo.children:
                if isinstance(i, MDCard):
                    await ak.sleep(0)
                    prestamo = (i.children[0].panel_cls.text).replace(
                        'Prestamo ', '') if not 'tarjeta' in i.children[0].panel_cls.text else 'tarjeta'
                    i.children[0].panel_cls.secondary_text = 'En esta cuenta: ' + \
                        "${:,.2f}".format(self.prestamos_list[prestamo])
                    ahorrau += abs(self.prestamos_list[prestamo])
            self.ids.ahorrado.text = 'Total ahorros: ' + "${:,.2f}".format(ahorrau)
        ak.start(refresh())

    def registro(self, operation, target):
        def clean_fields():
            self.dialogRegistro.content_cls.ids.monto.text = ''
            self.dialogRegistro.content_cls.ids.descripcion.text = ''

        def registrar(object):
            monto = self.dialogRegistro.content_cls.ids.monto.text
            descripcion = self.dialogRegistro.content_cls.ids.descripcion.text
            if self.validacion('monto', monto) and self.validacion('descripcion', descripcion):
                if 'tarjeta' in target:
                    saldo = self.prestamos_list['tarjeta']+eval(monto) if operation == 'ingresos' else self.prestamos_list['tarjeta']-eval(monto)
                    try:    
                        crud.update(f'fondo/{self.who}',{'tarjeta': str(saldo)})
                    except:
                        Snackbar(MDLabel(text="¡Ocurrió un error!")).open()
                        return None
                    clean_fields()
                    self.prestamos_list['tarjeta'] = saldo
                else:
                    saldo = self.prestamos_list[target]+eval(monto) if operation == 'ingresos' else self.prestamos_list[target]-eval(monto)
                    tarjeta = self.prestamos_list['tarjeta']+eval(monto) if operation == 'ingresos' else self.prestamos_list['tarjeta']-eval(monto)
                    try:
                        crud.push(f'fondo/{self.who}/prestamos/{target}/{operation}',{'fecha': descripcion, 'monto': monto})
                        crud.update(f'fondo/{self.who}',{'tarjeta': str(tarjeta)})
                    except:
                        Snackbar(MDLabel(text="¡Ocurrió un error!")).open()
                        return None
                    clean_fields()
                    self.prestamos_list[target] = saldo
                    self.prestamos_list['tarjeta'] = tarjeta
                self.dialogRegistro.dismiss()
            self.refresh()

        def cancelar(object):
            clean_fields()
            self.dialogRegistro.dismiss()

        self.dialogRegistro = MDDialog(
            title='Registrar '+operation,
            type='custom',
            content_cls=ContentGastos(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=registrar)]
        )
        self.dialogRegistro.open()
        target = target.replace('Prestamo ', '')
        self.dialogRegistro.content_cls.ids.descripcion.text = str(date.today())