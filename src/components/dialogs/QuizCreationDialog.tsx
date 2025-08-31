import React, { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Minus, Save, X, Upload, FileText } from "lucide-react";
import { Module } from "@/types/module";

interface QuizCreationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  module: Module | null;
  chapterId?: string;
  onQuizCreated?: () => void;
}

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

interface Quiz {
  id: string;
  title: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  questions: QuizQuestion[];
}

const QuizCreationDialog: React.FC<QuizCreationDialogProps> = ({
  open,
  onOpenChange,
  module,
  chapterId,
  onQuizCreated
}) => {
  const [quiz, setQuiz] = useState<Quiz>({
    id: "",
    title: "",
    difficulty: "beginner",
    questions: []
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadDifficulty, setUploadDifficulty] = useState<"beginner" | "intermediate" | "advanced">("beginner");

  // Reset quiz when dialog opens
  useEffect(() => {
    if (open && module) {
      setQuiz({
        id: "",
        title: "",
        difficulty: "beginner",
        questions: []
      });
      setUploadFile(null);
      setUploadTitle("");
      setUploadDifficulty("beginner");
    }
  }, [open, module]);

  const addQuestion = () => {
    const newQuestion: QuizQuestion = {
      id: Date.now().toString(),
      question: "",
      options: ["", "", "", ""],
      correctAnswer: 0,
      explanation: ""
    };
    setQuiz(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));
  };

  const removeQuestion = (questionId: string) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.filter(q => q.id !== questionId)
    }));
  };

  const updateQuestion = (questionId: string, field: keyof QuizQuestion, value: any) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === questionId ? { ...q, [field]: value } : q
      )
    }));
  };

  const updateQuestionOption = (questionId: string, optionIndex: number, value: string) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === questionId
          ? { ...q, options: q.options.map((opt, idx) => idx === optionIndex ? value : opt) }
          : q
      )
    }));
  };

  const saveManualQuiz = async () => {
    if (!module || !quiz.title || quiz.questions.length === 0) return;

    setSaving(true);
    try {
      const quizData = {
        ...quiz,
        chapter_id: chapterId,
        module_id: module.id
      };

      const response = await fetch(`/api/admin/modules/${module.id}/chapters/${chapterId}/quizzes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(quizData)
      });

      if (response.ok) {
        onOpenChange(false);
        onQuizCreated?.();
      }
    } catch (error) {
      console.error("Error saving quiz:", error);
    } finally {
      setSaving(false);
    }
  };

    const saveFileQuiz = async () => {
    if (!module || !uploadFile || !uploadTitle) return;

    setSaving(true);
    try {
      // Read file content as text
      const fileContent = await uploadFile.text();

      // Send as JSON instead of FormData
      const quizData = {
        title: uploadTitle,
        difficulty: uploadDifficulty,
        file_content: fileContent,
        file_name: uploadFile.name
      };

      const response = await fetch(`/api/admin/modules/${module.id}/chapters/${chapterId}/quizzes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(quizData)
      });

      if (response.ok) {
        const result = await response.json();
        onOpenChange(false);
        onQuizCreated?.();
        alert(`Quiz created successfully with ${result.questions_count} questions!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error("Error saving quiz:", error);
      alert("Error creating quiz from file");
    } finally {
      setSaving(false);
    }
  };

  const isValidManualQuiz = quiz.title.trim() && quiz.questions.length > 0 && quiz.questions.every(q =>
    q.question.trim() &&
    q.options.every(opt => opt.trim()) &&
    q.explanation.trim()
  );

  const isValidFileQuiz = uploadFile && uploadTitle.trim();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Quiz - {module?.title || module?.name}</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="manual" className="space-y-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="manual">Manual Creation</TabsTrigger>
            <TabsTrigger value="file">Upload TXT File</TabsTrigger>
          </TabsList>

          <TabsContent value="manual" className="space-y-6">
            {/* Quiz Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quiz Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="quiz-title">Quiz Title</Label>
                    <Input
                      id="quiz-title"
                      value={quiz.title}
                      onChange={(e) => setQuiz(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="Enter quiz title"
                    />
                  </div>
                  <div>
                    <Label htmlFor="difficulty">Difficulty Level</Label>
                    <Select
                      value={quiz.difficulty}
                      onValueChange={(value: any) => setQuiz(prev => ({ ...prev, difficulty: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="beginner">Beginner</SelectItem>
                        <SelectItem value="intermediate">Intermediate</SelectItem>
                        <SelectItem value="advanced">Advanced</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Questions */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-lg">Questions ({quiz.questions.length})</CardTitle>
                <Button onClick={addQuestion} size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Question
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                {quiz.questions.map((question, questionIndex) => (
                  <Card key={question.id} className="border-l-4 border-l-primary">
                    <CardHeader className="flex flex-row items-center justify-between">
                      <CardTitle className="text-base">Question {questionIndex + 1}</CardTitle>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeQuestion(question.id)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label>Question Text</Label>
                        <Textarea
                          value={question.question}
                          onChange={(e) => updateQuestion(question.id, "question", e.target.value)}
                          placeholder="Enter your question here"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Answer Options</Label>
                        {question.options.map((option, optionIndex) => (
                          <div key={optionIndex} className="flex items-center space-x-2">
                            <input
                              type="radio"
                              name={`correct-${question.id}`}
                              checked={question.correctAnswer === optionIndex}
                              onChange={() => updateQuestion(question.id, "correctAnswer", optionIndex)}
                            />
                            <Input
                              value={option}
                              onChange={(e) => updateQuestionOption(question.id, optionIndex, e.target.value)}
                              placeholder={`Option ${optionIndex + 1}`}
                            />
                          </div>
                        ))}
                      </div>

                      <div>
                        <Label>Explanation</Label>
                        <Textarea
                          value={question.explanation}
                          onChange={(e) => updateQuestion(question.id, "explanation", e.target.value)}
                          placeholder="Explain why this is the correct answer"
                        />
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {quiz.questions.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No questions added yet. Click "Add Question" to get started.
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button
                onClick={saveManualQuiz}
                disabled={!isValidManualQuiz || saving}
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? "Saving..." : "Save Quiz"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="file" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Upload Quiz from TXT File</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="file-title">Quiz Title</Label>
                    <Input
                      id="file-title"
                      value={uploadTitle}
                      onChange={(e) => setUploadTitle(e.target.value)}
                      placeholder="Enter quiz title"
                    />
                  </div>
                  <div>
                    <Label htmlFor="file-difficulty">Difficulty Level</Label>
                    <Select
                      value={uploadDifficulty}
                      onValueChange={(value: any) => setUploadDifficulty(value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="beginner">Beginner</SelectItem>
                        <SelectItem value="intermediate">Intermediate</SelectItem>
                        <SelectItem value="advanced">Advanced</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="quiz-file">TXT File</Label>
                  <Input
                    id="quiz-file"
                    type="file"
                    accept=".txt"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Upload a TXT file with quiz questions in the format:
                  </p>
                  <div className="text-xs text-muted-foreground bg-muted p-2 rounded mt-1 font-mono">
                    Question: What is the capital of France?<br/>
                    A) London<br/>
                    B) Paris<br/>
                    C) Berlin<br/>
                    D) Madrid<br/>
                    Answer: B
                  </div>
                </div>

                {uploadFile && (
                  <div className="flex items-center space-x-2 text-sm text-green-600">
                    <FileText className="w-4 h-4" />
                    <span>{uploadFile.name} selected</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button
                onClick={saveFileQuiz}
                disabled={!isValidFileQuiz || saving}
              >
                <Upload className="w-4 h-4 mr-2" />
                {saving ? "Creating..." : "Create Quiz from File"}
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default QuizCreationDialog;
