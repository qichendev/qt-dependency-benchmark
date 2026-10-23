#include <QCoreApplication>
#include <QString>
#include <QVersionNumber>
#include <iostream>

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);
    const auto version = QVersionNumber::fromString(QString::fromLatin1(qVersion()));
    std::cout << "Qt Core " << qVersion() << '\n';
    return version == QVersionNumber(6, 11, 1) ? 0 : 1;
}
