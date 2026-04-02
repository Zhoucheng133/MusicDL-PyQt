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

    property bool loading: false;

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
    function searchHanlder() {
        if(loading){
            return
        }
        if (searchInput.text.length == 0) {
            errDialog.dialogTitle = "无法搜索"
            errDialog.dialogBody = "输入关键词不能为空"
            errDialog.open()
        } else {
            loading=true
            core.search(searchInput.text, comboBox.currentText)
        }
    }

    Connections {
        target: core
        // 监听 listChanged 信号
        function onListChanged() {
            loading = false // 收到列表更新信号后，停止转圈
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
                enabled: !loading
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

        Label {
            Layout.fillWidth: true
            text: "输入关键词搜索"
            color: "gray"
            visible: core.searchResult.length === 0
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }
        Repeater {
            model: core.searchResult
            delegate: Label { text: modelData['search']['ar'][0]['name'] }
        }

        Item { Layout.fillHeight: true }
    }
}