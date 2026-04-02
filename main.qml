import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 600
    height: 500
    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    Material.primary: Material.Teal
    Material.accent: Material.Teal

    Dialog {
        id: errDialog

        property string dialogTitle: ""
        property string dialogBody: ""

        title: dialogTitle
        width: 400
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok

        Label {
            text: errDialog.dialogBody
            padding: 20
        }
    }

    function searchHanlder(){
        if(searchInput.length==0){
            errDialog.dialogTitle = "无法搜索"
            errDialog.dialogBody = "输入关键词不能为空"
            errDialog.open()
        }
    }


    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        RowLayout{
            Layout.fillWidth: true
            spacing: 15

            ComboBox {
                id: comboBox
                Layout.preferredHeight: 40
                Layout.preferredWidth: 200
                model: [
                    "NeteaseMusicClient",
                    "MiguMusicClient",
                    "QQMusicClient",
                    "KuwoMusicClient",
                    "QianqianMusicClient"
                ]
             }

            TextField {
                id: searchInput
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                onAccepted: {
                    searchHanlder()
                }
            }

            Button {
                text: "搜索"
                Layout.preferredHeight: 50
                highlighted: true
                onClicked: {
                    searchHanlder()
                }
            }
        }

        RowLayout{
            Layout.preferredHeight: 40
            Layout.fillWidth: true
            spacing: 5

            Rectangle {
                Layout.preferredHeight: parent.height
                Layout.preferredWidth: 40
                color: Material.primary

                Label {
                    text: "#"
                    anchors.centerIn: parent
                    color: "white"
                }
            }

            Rectangle {
                Layout.preferredHeight: parent.height
                Layout.fillWidth: true
                color: Material.primary

                Label {
                    text: "标题"
                    anchors.centerIn: parent
                    color: "white"
                }
            }

            Rectangle {
                Layout.preferredHeight: parent.height
                Layout.preferredWidth: 150
                color: Material.primary

                Label {
                    text: "艺人"
                    anchors.centerIn: parent
                    color: "white"
                }
            }

            Rectangle {
                Layout.preferredHeight: parent.height
                Layout.preferredWidth: 50
                color: Material.primary

                Label {
                    text: "操作"
                    anchors.centerIn: parent
                    color: "white"
                }
            }
        }



        Item { Layout.fillHeight: true }
    }
}