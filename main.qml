import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 400
    height: 500
    title: "Fluent UI Example"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        Text {
            text: "设置"
            font.pixelSize: 28
            font.weight: Font.DemiBold
            Layout.alignment: Qt.AlignLeft
        }

        RowLayout {
            Layout.fillWidth: true
            Text { 
                text: "开启深色模式"
                Layout.fillWidth: true 
            }
            Switch {
                checked: true
                onToggled: console.log("Switch state:", checked)
            }
        }

        Button {
            text: "确认提交"
            highlighted: true // Fluent 风格的高亮色
            Layout.fillWidth: true
            onClicked: {
                // 执行逻辑
            }
        }

        Item { Layout.fillHeight: true } // 类似 Spacer()
    }
}