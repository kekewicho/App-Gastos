from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivy.utils import platform
from kivymd.uix.card import MDSeparator
import crud
from widgets.widgets import OPItem, ContentGastos, DiferidoContent
from kivymd.utils import asynckivy as ak
from kivy.properties import NumericProperty
from kivymd.uix.snackbar import Snackbar
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase
from kivy.uix.scrollview import ScrollView
import os

Builder.load_file(os.path.join("screens","screenGastos","screenGastos.kv"))

class Tabs(ScrollView, MDTabsBase):
    pass


class ScreenGastos(MDScreen):
    balance = NumericProperty(0)
    actual = ''
    who = 'luis' if not (platform in ['macosx','ios']) else 'joss'
    dialog = None

    def ingre_egre_init_consulta(self):
        async def ingre_egre_init_consulta():
            self.ids.lblUser.text += 'Luisito!' if not (platform in ['macosx','ios']) else 'Joselincita! <3'
            self.actual = crud.quince_actual('new')
            quincena_actual = crud.translate_codigo(self.actual)
            self.ids.quincena.text = quincena_actual
            # construyendo la pagina de las cuentas quincenales
            for operation in ('ingresos', 'egresos'):
                data = crud.get(f'ingre_egre/{self.who}/{self.actual}/{operation}')
                if data is None:
                    pass
                else:
                    for key,value in data.items():
                        await ak.sleep(0)
                        if operation == 'ingresos':
                            self.balance += eval(value['monto'])
                            self.add_opitem('ingresos', value['monto'], value[
                                            'descripcion'], key)
                        elif operation == 'egresos':
                            self.balance -= eval(value['monto'])
                            self.add_opitem('egresos', value['monto'], value[
                                            'descripcion'], key)
        ak.start(ingre_egre_init_consulta())

    def add_opitem(self, operation, monto, descripcion, key):
        async def add_opitem():
            self.ids[operation].add_widget(MDSeparator())
            item = OPItem(
                monto='$'+monto,
                descripcion=descripcion,
                key=key,
                op=operation
            )
            self.ids[operation].add_widget(item)
        ak.start(add_opitem())

    def delete_opitem(self, item, event, op, monto):
        def deleteItem(object):
            crud.remove(f'ingre_egre/{self.who}/{self.actual}/{op}/{event}')
            monto_ = monto.replace('$', '').replace(',', '')
            if op == 'ingresos':
                self.balance -= eval(monto_)
            if op == 'egresos':
                self.balance += eval(monto_)
            self.ids[op].remove_widget(item)
            self.dialog.dismiss()

        def cancelar(object):
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title='¿Eliminar operación?',
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Eliminar', on_release=deleteItem,theme_text_color="Custom",
                        text_color="#a80000",)]
        )
        self.dialog.open()

    def edit_op(self, event, operation, wdg):
        monto_before = eval((wdg.monto).replace('$', '').replace(',', ''))

        def registrar(object):
            monto, descripcion = self.dialog.content_cls.get_data()
            if self.validacion('monto', monto) and self.validacion('descripcion', descripcion):
                if monto_before == monto:
                    self.dialog.dismiss()
                    return None
                try:
                    crud.update(f'ingre_egre/{self.who}/{self.actual}/{operation}/{event}',{'monto': monto, 'descripcion': descripcion})
                except:
                    Snackbar(MDLabel(text="¡Ocurrió un error!")).open()
                    return None
                self.dialog.content_cls.clean_fields()
                dif = abs(monto_before-eval(monto))
                if monto_before > eval(monto):
                    if operation == 'egresos':
                        self.balance += dif
                    if operation == 'ingresos':
                        self.balance -= dif
                if monto_before < eval(monto):
                    if operation == 'egresos':
                        self.balance -= dif
                    if operation == 'ingresos':
                        self.balance += dif
                wdg.monto = str("$"+monto)
                wdg.descripcion = descripcion
                self.dialog.dismiss()
            else:
                self.dialog.content_cls.ids.monto.error = True
                self.dialog.content_cls.ids.descripcion.error = True

        def cancelar(object):
            self.dialog.content_cls.clean_fields()
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title='Modificar gasto',
            type='custom',
            content_cls=ContentGastos(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=registrar)]
        )
        self.dialog.content_cls.ids.monto.text = (
            wdg.monto).replace('$', '').replace(',', '')
        self.dialog.content_cls.ids.descripcion.text = wdg.descripcion
        self.dialog.open()

    def trasladar_quincena(self, direction):
        async def trasladar_quincena():
            self.balance = 0
            a = crud.quince_actual('valor', direction, self.actual)
            self.ids.quincena.text = crud.translate_codigo(a)
            self.actual = a
            await ak.sleep(0)
            for operation in ('ingresos', 'egresos'):
                self.ids[operation].clear_widgets()
                data = crud.get(f'ingre_egre/{self.who}/{self.actual}/{operation}')
                if data is None:
                    pass
                else:
                    for key,value in data.items():
                        await ak.sleep(0)
                        if operation == 'ingresos':
                            self.balance += eval(value['monto'])
                            self.add_opitem('ingresos',value['monto'],value['descripcion'],key)
                        elif operation == 'egresos':
                            self.balance -= eval(value['monto'])
                            self.add_opitem('egresos',value['monto'],value['descripcion'],key)
        ak.start(trasladar_quincena())

    def registro(self, operation):
        def registrar(object):
            monto, descripcion = self.dialog.content_cls.get_data()
            if self.validacion('monto', monto) and self.validacion('descripcion', descripcion):
                try:
                    a = crud.push(f'ingre_egre/{self.who}/{self.actual}/{operation}',{'monto': monto, 'descripcion': descripcion})
                except:
                    Snackbar(MDLabel(text="¡Ocurrió un error!")).open()
                    return None
                self.add_opitem(operation, monto, descripcion, a['name'])
                self.dialog.content_cls.clean_fields()
                if operation == 'ingresos':
                    self.balance += eval(monto)
                elif operation == 'egresos':
                    self.balance -= eval(monto)
                self.dialog.dismiss()
            else:
                self.dialog.content_cls.ids.monto.error = True
                self.dialog.content_cls.ids.descripcion.error = True

        def cancelar(object):
            self.dialog.content_cls.clean_fields()
            self.dialog.dismiss()

        self.ids.speed_dial.close_stack()
        self.dialog = MDDialog(
            title='Registrar '+operation,
            type='custom',
            content_cls=ContentGastos(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=registrar)]
        )
        self.dialog.open()

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


    def registroDiferido(self):
        def registrar(object):
            pago=self.dialog.content_cls.pagoPorPeriodo()
            descripcion=self.dialog.content_cls.ids.descripcion.text
            counter=1
            quinceList=self.dialog.content_cls.getQuincenas()
            cantQuince=len(quinceList)
            for quincena in quinceList:
                data={
                    'descripcion':f'{descripcion} {counter}/{cantQuince}',
                    'monto':str(pago)
                }
                registro=crud.push(f'ingre_egre/{self.who}/{quincena}/egresos',data)
                counter+=1

                if quincena==self.actual:
                    self.add_opitem('egresos',str(pago),f'{descripcion} {counter}/{cantQuince}',registro['name'])

        def cancelar(object):
            self.dialog.content_cls.clean_fields()
            self.dialog.dismiss()

        self.ids.speed_dial.close_stack()
        self.dialog = MDDialog(
            title='Registrar diferido',
            type='custom',
            content_cls=DiferidoContent(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=registrar)]
        )
        self.dialog.open()