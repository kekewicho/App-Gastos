from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import StringProperty
from kivy.utils import platform
from kivymd.uix.card import MDSeparator
import crud
from threading import Thread
from kivy.clock import mainthread
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from widgets.widgets import Cards,Buttons,ContentNvoPrestamo,Content


class screenFondo(MDScreen):
    ahorro=0
    prestamos_list={}

    def fondo_init_consulta(self):
        # construyendo la pagina de ahorros
        global ahorro, prestamos_list
        tarjeta = crud.db.child(f'fondo/{self.who}').child('tarjeta').get()
        self.update_tarjeta(tarjeta)
        prestamos = crud.db.child(f'fondo/{self.who}/prestamos').get()
        ahorro += eval(tarjeta.val())
        prestamos_list['tarjeta'] = eval(tarjeta.val())
        for i in prestamos.each():
            saldo = 0
            for j in ('ingresos', 'egresos'):
                op = crud.db.child(
                    f'fondo/{self.who}').child('prestamos').child(i.key()).child(j).get()
                if op.each() is None:
                    pass
                else:
                    for h in op.each():
                        if j == 'ingresos':
                            saldo += eval(h.val()['monto'])
                        else: saldo -= eval(h.val()['monto'])
            ahorro += abs(saldo)
            prestamos_list[i.key()] = saldo
            self.fondo_init_construction(i.key(), saldo)
        self.update_ahorrado(ahorro)

    @mainthread
    def update_ahorrado(self, ahorro):
        self.root.ids.ahorrado.text = 'Total ahorrado: '+"${:,.2f}".format(ahorro)

    @mainthread
    def update_tarjeta(self, tarjeta):
        card = Cards()
        content = Buttons()
        card.add_widget(
            MDExpansionPanel(
                    content=content,
                        panel_cls=MDExpansionPanelTwoLine(text='En tarjeta del banco', secondary_text='En esta cuenta: '+"${:,.2f}".format(eval(tarjeta.val()))),
                )
        )
        self.root.ids.layout_fondo.add_widget(card)

    @mainthread
    def fondo_init_construction(self, key,saldo):
        card = Cards()
        content = Buttons()
        card.add_widget(
            MDExpansionPanel(
                    content=content,
                panel_cls=MDExpansionPanelTwoLine(text='Prestamo '+key, secondary_text='En esta cuenta: '+"${:,.2f}".format(saldo),
                                                  )
                    ))
        self.root.ids.layout_fondo.add_widget(card)


    def nuevo_prestamo(self):
        def clean_fields():
            self.dialog.content_cls.ids.descripcion.text = ''

        def registrar(object):
            global prestamos_list
            nombre = self.dialog.content_cls.ids.descripcion.text
            who = 'luis' if platform != 'macosx' else 'joss'
            crud.db.child(
                f'fondo/{who}').child('prestamos').child(nombre).set('')
            card = Cards()
            content = Buttons()
            card.add_widget(
                MDExpansionPanel(
                    content=content,
                    panel_cls=MDExpansionPanelTwoLine(text='Prestamo '+nombre, secondary_text='En esta cuenta: '+"${:,.2f}".format(0),
                                                      )
                ))
            self.ids.layout_fondo.add_widget(card)
            prestamos_list[nombre] = 0
            self.dialog.dismiss()

        def cancelar(object):
            clean_fields()
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title='Nuevo préstamo',
            text='Nota: No uses la palabra "Prestamo"',
            type='custom',
            content_cls=ContentNvoPrestamo(),
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

    who = 'luis' if platform != 'macosx' else 'joss'

    def refresh(self):
        global prestamos_list
        ahorrau = 0
        for i in self.parent.parent.parent.children:
            if isinstance(i, MDCard):
                prestamo = (i.children[0].panel_cls.text).replace(
                    'Prestamo ', '') if not 'tarjeta' in i.children[0].panel_cls.text else 'tarjeta'
                i.children[0].panel_cls.secondary_text = 'En esta cuenta: ' + \
                    "${:,.2f}".format(prestamos_list[prestamo])
                ahorrau += abs(prestamos_list[prestamo])
        self.parent.parent.parent.children[-1].children[0].text = 'Total ahorros: ' + \
            "${:,.2f}".format(ahorrau)

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

    def registro(self, operation, target):
        def clean_fields():
            self.dialog.content_cls.ids.monto.text = ''
            self.dialog.content_cls.ids.descripcion.text = ''

        def registrar(object):
            global prestamos_list, ahorro
            monto = self.dialog.content_cls.ids.monto.text
            descripcion = self.dialog.content_cls.ids.descripcion.text
            who = 'luis' if platform != 'macosx' else 'joss'
            if self.validacion('monto', monto) and self.validacion('descripcion', descripcion):
                ahorro += eval(monto) if self.operation == 'ingresos' else eval(monto)*-1
                if 'tarjeta' in self.target:
                    saldo = prestamos_list['tarjeta']+eval(
                        monto) if self.operation == 'ingresos' else prestamos_list['tarjeta']-eval(monto)
                    crud.db.child(
                        f'fondo/{who}').update({'tarjeta': str(saldo)})
                    clean_fields()
                    prestamos_list['tarjeta'] = saldo
                else:
                    saldo = prestamos_list[self.target]+eval(
                        monto) if self.operation == 'ingresos' else prestamos_list[self.target]-eval(monto)
                    tarjeta = prestamos_list['tarjeta']+eval(
                        monto) if self.operation == 'ingresos' else prestamos_list['tarjeta']-eval(monto)
                    crud.db.child(f'fondo/{who}').child('prestamos').child(self.target).child(
                        self.operation).push({'fecha': descripcion, 'monto': monto})
                    crud.db.child(
                        f'fondo/{who}').update({'tarjeta': str(tarjeta)})
                    clean_fields()
                    prestamos_list[self.target] = saldo
                    prestamos_list['tarjeta'] = tarjeta
                self.refresh()
                self.dialog.dismiss()

        def cancelar(object):
            clean_fields()
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title='Registrar '+operation,
            type='custom',
            content_cls=Content(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=registrar)]
        )
        self.dialog.open()
        self.operation = operation
        self.target = target.replace('Prestamo ', '')
        self.dialog.content_cls.ids.descripcion.text = str(
            crud.datetime.date.today())