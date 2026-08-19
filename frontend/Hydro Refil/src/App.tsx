import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/ui/Navbar';
import { Footer } from './components/ui/Footer';
import { Dashboard } from './pages/Dashboard';
import { NewAssessment } from './pages/NewAssessment';
import { AssessmentDetail } from './pages/AssessmentDetail';
import { AssessmentList } from './pages/AssessmentList';
import { ReportView } from './pages/ReportView';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100 font-sans selection:bg-sky-500 selection:text-white">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assessment/new" element={<NewAssessment />} />
            <Route path="/assessment/:id" element={<AssessmentDetail />} />
            <Route path="/assessment/:id/report" element={<ReportView />} />
            <Route path="/assessments" element={<AssessmentList />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}