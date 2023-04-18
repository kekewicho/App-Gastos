# App-Gastos
App para control de gastos conectada a base de datos en Firebase. Incluye manejo de ingresos y egresos quincenal, apartado para sección de ahorros y herramientas para la administración de las finanzas con tu pareja.

La app esta hecha como proyecto personal (Por lo que cubre mis necesidades) por lo cual uso algunos chistes locales (Just a joke) y actualmente se encuentra funcional en un iOS y Android, comunicadas por una base de datos Realtime Databse de [Firebase](https://firebase.google.com/ "Firebase Home Page").

La interfaz está construida con [Kivy](https://github.com/kivy/kivy "Kivy Github")/[KivyMD](https://github.com/kivymd/KivyMD "KivyMD Github").

## Screenshots

<div>
  <img src="https://github.com/kekewicho/App-Gastos/blob/main/screenshots/Imagen1.jpeg" alt="Pantalla Gastos" style="float: left; margin-right: 50px; width: 25%;">
  <img src="https://github.com/kekewicho/App-Gastos/blob/main/screenshots/Imagen2.jpeg" alt="Navigation Menu" style="float: left; margin-right: 50px; width: 25%;">
  <img src="https://github.com/kekewicho/App-Gastos/blob/main/screenshots/Imagen3.jpeg" alt="Pantalla Gastos Concubinos" style="float: left; margin-right: 50px; width: 25%;">
</div>

## About
Recién me independicé y me di cuenta que la nueva vida de adulto puede ser difícil de sobrellevar, sobre todo en lo económico, entre planes de pagos fuera de presupuesto, etc. Además, cuando por fin lograba ahorrar algo, duraba muy poco sin gastar de ello, con la promesa de reponerlo, pero la verdad es que nunca lograba recordar en donde se iba. Es por ello que hice mi propia app para tener un control sobre mis finanzas personales, permitiéndome planificar el presupuesto de cada quincena y visualizar cual es mi margen para cada ciclo.

Finalmente, tratando de abarcar las bondades de un control sobre las finanzas de esa manera, fue que decidí incorporar una herramienta que nos permitiera a mi y a mi pareja esa administración tanto personal con en los gastos de la casa, donde incluí la lista de la despensa y los gastos mutuos.


## Features

  ### **Control de gatos quincenales**
   * Edición de operaciones (monto o descripcion)
   * Eliminación de operaciones
   * Traslado por quincenas, a quincena anterior o posterior
  ---
  ### **Administración de ahorros (Fondo)**
   * Creación de nuevo prestamo
   * Actualización de balances con respecto a una cuenta pivot donde se asume que guardas tus ahorros (Tarjeta)
   * Actualización de cada prestamo con abonos o prestamos
  ---
  ### **Administración del hogar**
   * Registro de cuentas mutuas
   * Actualización de balance para ver quien le debe a quien
  
