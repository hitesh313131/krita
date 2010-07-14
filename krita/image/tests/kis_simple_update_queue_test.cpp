/*
 *  Copyright (c) 2010 Dmitry Kazakov <dimula73@gmail.com>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include "kis_simple_update_queue_test.h"
#include <qtest_kde.h>

#include <KoColorSpace.h>
#include <KoColorSpaceRegistry.h>

#include "kis_merge_walker.h"
#include "kis_simple_update_queue.h"

bool checkWalker(KisBaseRectsWalkerSP walker, const QRect &rect) {
    if(walker->requestedRect() == rect) {
        return true;
    }
    else {
        qDebug() << "walker rect:" << walker->requestedRect();
        qDebug() << "expected rect:" << rect;
        return false;
    }
}

void KisSimpleUpdateQueueTest::testJobProcessing()
{
    KisTestableUpdaterContext context(2);

    QRect imageRect(0,0,200,200);

    const KoColorSpace * cs = KoColorSpaceRegistry::instance()->rgb8();
    KisImageSP image = new KisImage(0, imageRect.width(), imageRect.height(), cs, "merge test");

    KisPaintLayerSP paintLayer = new KisPaintLayer(image, "test", OPACITY_OPAQUE_U8);

    image->lock();
    image->addNode(paintLayer);
    image->unlock();

    QRect dirtyRect1(0,0,50,100);
    QRect dirtyRect2(0,0,100,100);
    QRect dirtyRect3(50,0,50,100);
    QRect dirtyRect4(150,150,50,50);

    QVector<KisUpdateJobItem*> jobs;
    KisWalkersList walkersList;

    /**
     * Process the queue and look what has been added into
     * the updater context
     */

    KisTestableSimpleUpdateQueue queue;

    queue.addJob(paintLayer, dirtyRect1, imageRect);
    queue.addJob(paintLayer, dirtyRect2, imageRect);
    queue.addJob(paintLayer, dirtyRect3, imageRect);
    queue.addJob(paintLayer, dirtyRect4, imageRect);

    queue.processQueue(context);

    jobs = context.getJobs();

    QVERIFY(checkWalker(jobs[0]->walker(), dirtyRect4));
    QVERIFY(checkWalker(jobs[1]->walker(), dirtyRect2));
    QCOMPARE(jobs.size(), 2);

    walkersList = queue.getWalkersList();

    QCOMPARE(walkersList.size(), 0);


    /**
     * Test blocking the process
     */

    context.clear();

    queue.blockProcessing(context);

    queue.addJob(paintLayer, dirtyRect1, imageRect);
    queue.addJob(paintLayer, dirtyRect2, imageRect);
    queue.addJob(paintLayer, dirtyRect3, imageRect);
    queue.addJob(paintLayer, dirtyRect4, imageRect);

    jobs = context.getJobs();
    QCOMPARE(jobs[0]->walker(), KisBaseRectsWalkerSP(0));
    QCOMPARE(jobs[1]->walker(), KisBaseRectsWalkerSP(0));

    queue.startProcessing(context);

    jobs = context.getJobs();

    QVERIFY(checkWalker(jobs[0]->walker(), dirtyRect4));
    QVERIFY(checkWalker(jobs[1]->walker(), dirtyRect2));
}

void KisSimpleUpdateQueueTest::testSplit()
{
    QRect imageRect(0,0,1024,1024);

    const KoColorSpace * cs = KoColorSpaceRegistry::instance()->rgb8();
    KisImageSP image = new KisImage(0, imageRect.width(), imageRect.height(), cs, "merge test");

    KisPaintLayerSP paintLayer = new KisPaintLayer(image, "test", OPACITY_OPAQUE_U8);

    image->lock();
    image->addNode(paintLayer);
    image->unlock();

    QRect dirtyRect1(0,0,1000,1000);

    KisTestableSimpleUpdateQueue queue;
    KisWalkersList& walkersList = queue.getWalkersList();

    queue.addJob(paintLayer, dirtyRect1, imageRect);

    QCOMPARE(walkersList.size(), 4);
    QVERIFY(checkWalker(walkersList[0], QRect(512,512,488,488)));
    QVERIFY(checkWalker(walkersList[1], QRect(0,512,512,488)));
    QVERIFY(checkWalker(walkersList[2], QRect(512,0,488,512)));
    QVERIFY(checkWalker(walkersList[3], QRect(0,0,512,512)));

    queue.optimize();

    //must change nothing

    QCOMPARE(walkersList.size(), 4);
    QVERIFY(checkWalker(walkersList[0], QRect(512,512,488,488)));
    QVERIFY(checkWalker(walkersList[1], QRect(0,512,512,488)));
    QVERIFY(checkWalker(walkersList[2], QRect(512,0,488,512)));
    QVERIFY(checkWalker(walkersList[3], QRect(0,0,512,512)));
}

QTEST_KDEMAIN(KisSimpleUpdateQueueTest, NoGUI)
#include "kis_simple_update_queue_test.moc"

