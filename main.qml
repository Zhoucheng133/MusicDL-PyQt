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

    title: "musicdl GUI"

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

        function onSearchError(msg){
            loading = false
            errDialog.dialogTitle = "错误"
            errDialog.dialogBody = msg
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
                Layout.preferredWidth: 70
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
            Layout.fillHeight: true
            text: "输入关键词搜索"
            color: "gray"
            visible: core.searchResult.length === 0 && !loading
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            Layout.bottomMargin: 20
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: loading

            Item { Layout.fillHeight: true }

            BusyIndicator {
                Layout.fillWidth: true
                id: busyIndicator
                running: true
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 40
                Layout.preferredHeight: 40
            }

            Item { Layout.fillHeight: true }
        }

        ScrollView{
            id: scrollList
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !loading
            clip: true
            ColumnLayout {
                width: scrollList.availableWidth
                Layout.fillWidth: true
                Repeater {
                    model: core.searchResult
                    visible: !loading
                    delegate: RowLayout{
                        Layout.preferredHeight: 45
                        Layout.fillWidth: true

                        Rectangle {
                            Layout.preferredHeight: parent.height
                            Layout.preferredWidth: 40
                            color: "transparent"

                            Label {
                                text: index+1
                                anchors.centerIn: parent
                            }
                        }

                        Rectangle {
                            Layout.preferredHeight: parent.height
                            Layout.fillWidth: true
                            color: "transparent"

                            Label {
                                text: modelData['name']
                                anchors.centerIn: parent
                                width: parent.width * 0.9
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                            }
                        }

                        Rectangle {
                            Layout.preferredHeight: parent.height
                            Layout.preferredWidth: 150
                            color: "transparent"

                            Label {
                                text: modelData['artist']
                                anchors.centerIn: parent
                                width: parent.width * 0.9
                                horizontalAlignment: Text.AlignHCenter
                                elide: Text.ElideRight
                            }
                        }

                        Rectangle {
                            Layout.preferredHeight: parent.height
                            Layout.preferredWidth: 70
                            color: "transparent"
                            // color: "red"
                            Button {
                                Layout.fillWidth: true
                                anchors.centerIn: parent
                                height: parent.height
                                text: "下载"
                                flat: true
                                onClicked: core.download(index)
                            }
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
}