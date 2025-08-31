import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { MessageCircle, Send, Bot, User, Loader2, AlertCircle } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  metadata?: {
    chunks_found?: number;
    department?: string;
    department_id?: string;
  };
}

interface DepartmentOption {
  id: string;
  name: string;
  description: string;
}

interface ConversationAgentProps {
  departmentId: string;
  departmentName: string;
  userId?: string;
}

const ConversationAgent: React.FC<ConversationAgentProps> = ({
  departmentId,
  departmentName,
  userId = 'current_user'
}) => {
  // Debug component initialization
  useEffect(() => {
    console.log(`[ConversationAgent] Component initialized with:`);
    console.log(`  - departmentId: ${departmentId}`);
    console.log(`  - departmentName: ${departmentName}`);
    console.log(`  - userId: ${userId}`);
  }, [departmentId, departmentName, userId]);
  // Core state
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Department state - start with no department detected
  const [currentDepartment, setCurrentDepartment] = useState<{
    name: string;
    id: string;
    isDetected: boolean;
  }>({
    name: departmentName || '',
    id: departmentId || '',
    isDetected: !!(departmentName && departmentName.trim())
  });

  // Error state
  const [hasDepartmentError, setHasDepartmentError] = useState(false);
  const [fallbackOptions, setFallbackOptions] = useState<DepartmentOption[]>([]);

  // Refs
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize welcome message
  useEffect(() => {
    if (!isInitialized && isOpen) {
      const welcomeMessage: Message = {
        id: 'welcome',
        type: 'agent',
        content: currentDepartment.isDetected
          ? `Hello! I'm your ${currentDepartment.name} onboarding assistant. I can help answer questions about department policies, procedures, and documentation. What would you like to know?`
          : `Hello! I'm your onboarding assistant. I'll automatically detect your department when you ask questions. What would you like to know?`,
        timestamp: new Date(),
        metadata: {
          department: currentDepartment.name,
          department_id: currentDepartment.id
        }
      };
      setMessages([welcomeMessage]);
      setIsInitialized(true);
    }
  }, [isOpen, isInitialized, currentDepartment]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  // Update current department when props change (only if not already detected)
  useEffect(() => {
    if (!currentDepartment.isDetected && departmentName && departmentName.trim()) {
      console.log(`[ConversationAgent] Updating from props: ${departmentName}`);
      setCurrentDepartment({
        name: departmentName,
        id: departmentId || '',
        isDetected: true
      });
    }
  }, [departmentId, departmentName, currentDepartment.isDetected]);

  // Debug department state changes
  useEffect(() => {
    console.log(`[ConversationAgent] Department state changed:`, currentDepartment);
    console.log(`[ConversationAgent] Header should show: ${currentDepartment.isDetected ? `${currentDepartment.name} Assistant` : 'Onboarding Assistant'}`);
  }, [currentDepartment]);

  const updateDepartment = useCallback((name: string, id: string) => {
    console.log(`[ConversationAgent] updateDepartment called with: ${name}, ${id}`);
    setCurrentDepartment({
      name,
      id,
      isDetected: true
    });
    setHasDepartmentError(false);
  }, []);

  const handleDepartmentError = useCallback((error: string, options?: DepartmentOption[]) => {
    setHasDepartmentError(true);
    if (options) {
      setFallbackOptions(options);
    }

    const errorMessage: Message = {
      id: `error_${Date.now()}`,
      type: 'agent',
      content: error,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, errorMessage]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    console.log(`[ConversationAgent] Sending message for user: ${userId}`);
    console.log(`[ConversationAgent] Current department state:`, currentDepartment);

    try {
      const requestData = {
        question: userMessage.content,
        user_id: userId
      };

      console.log(`[ConversationAgent] Request data:`, requestData);

      const response = await fetch('/api/conversation/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      console.log(`[ConversationAgent] Response status: ${response.status}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`[ConversationAgent] Response data:`, data);

      if (data.success) {
        const agentMessage: Message = {
          id: `agent_${Date.now()}`,
          type: 'agent',
          content: data.answer,
          timestamp: new Date(),
          metadata: {
            chunks_found: data.chunks_found,
            department: data.department,
            department_id: data.department_id
          }
        };
        setMessages(prev => [...prev, agentMessage]);

        // Update department if detected from backend
        console.log(`[ConversationAgent] Checking department update:`);
        console.log(`  - data.department: ${data.department}`);
        console.log(`  - data.department_id: ${data.department_id}`);
        console.log(`  - currentDepartment.name: ${currentDepartment.name}`);
        console.log(`  - Should update: ${data.department && data.department !== currentDepartment.name}`);

        if (data.department && data.department !== currentDepartment.name) {
          console.log(`[ConversationAgent] Updating department to: ${data.department}`);
          updateDepartment(data.department, data.department_id || currentDepartment.id);
        } else {
          console.log(`[ConversationAgent] No department update needed`);
        }
      } else {
        // Handle department detection errors
        if (data.error === 'Department not assigned') {
          console.log(`[ConversationAgent] Department not assigned error`);
          handleDepartmentError(
            data.answer || 'Your profile doesn\'t have a department assigned. Please contact your administrator to update your profile with department information.',
            data.fallback_options
          );
        } else {
          throw new Error(data.error || 'Failed to get response');
        }
      }
    } catch (error) {
      console.error('[ConversationAgent] Error sending message:', error);
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        type: 'agent',
        content: `I'm sorry, I encountered an error while processing your question. Please try again. Error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);

      toast({
        title: "Error",
        description: "Failed to get response from assistant",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
      // Focus back to input
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const selectFallbackDepartment = (department: DepartmentOption) => {
    updateDepartment(department.name, department.id);
    setFallbackOptions([]);

    const confirmationMessage: Message = {
      id: `confirmation_${Date.now()}`,
      type: 'agent',
      content: `Great! I've set your department to ${department.name}. How can I help you with ${department.name} onboarding?`,
      timestamp: new Date(),
      metadata: {
        department: department.name,
        department_id: department.id
      }
    };
    setMessages(prev => [...prev, confirmationMessage]);
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-shadow"
        >
          <MessageCircle className="w-6 h-6" />
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Card className="w-96 h-[500px] shadow-2xl">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-blue-600" />
              <div>
                <CardTitle className="text-sm">
                  {(() => {
                    const headerText = currentDepartment.isDetected
                      ? `${currentDepartment.name} Assistant`
                      : 'Onboarding Assistant';
                    console.log(`[ConversationAgent] Header rendering: "${headerText}" (detected: ${currentDepartment.isDetected}, name: "${currentDepartment.name}")`);
                    return headerText;
                  })()}
                  {hasDepartmentError && (
                    <AlertCircle className="w-4 h-4 text-orange-500 inline ml-1" />
                  )}
                </CardTitle>
                <CardDescription className="text-xs">
                  {currentDepartment.isDetected
                    ? `Ask me anything about ${currentDepartment.name}`
                    : 'Ask me anything about your department'
                  }
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="h-6 w-6 p-0"
              >
                ×
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-0 flex flex-col h-[calc(100%-80px)]">
          <ScrollArea className="flex-1 px-4" ref={scrollAreaRef}>
            <div className="space-y-4 py-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.type === 'agent' && (
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="bg-blue-100 text-blue-600">
                        <Bot className="w-4 h-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}

                  <div className={`max-w-[80%] ${message.type === 'user' ? 'order-first' : ''}`}>
                    <div
                      className={`rounded-lg px-3 py-2 text-sm ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      {message.type === 'agent' ? (
                        <div className="prose prose-sm max-w-none">
                          <ReactMarkdown>
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        message.content
                      )}
                    </div>

                    {message.metadata && (
                      <div className="flex items-center gap-2 mt-1">
                        {message.metadata.chunks_found !== undefined && (
                          <Badge variant="secondary" className="text-xs">
                            {message.metadata.chunks_found} sources
                          </Badge>
                        )}
                        <span className="text-xs text-gray-500">
                          {message.timestamp.toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                    )}
                  </div>

                  {message.type === 'user' && (
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="bg-gray-600 text-white">
                        <User className="w-4 h-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              ))}

              {/* Fallback department selection */}
              {fallbackOptions.length > 0 && (
                <div className="flex gap-3 justify-start">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-blue-100 text-blue-600">
                      <Bot className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="max-w-[80%]">
                    <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm text-gray-900">
                      <p className="mb-2">Please select your department to continue:</p>
                      <div className="space-y-1">
                        {fallbackOptions.map((dept) => (
                          <Button
                            key={dept.id}
                            variant="outline"
                            size="sm"
                            onClick={() => selectFallbackDepartment(dept)}
                            className="w-full justify-start text-xs"
                          >
                            {dept.name}
                          </Button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-blue-100 text-blue-600">
                      <Bot className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-gray-100 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm text-gray-600">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  hasDepartmentError
                    ? "Select your department first..."
                    : "Ask a question about your department..."
                }
                disabled={isLoading || hasDepartmentError}
                className="flex-1"
              />
              <Button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading || hasDepartmentError}
                size="sm"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <div className="text-xs text-gray-500 mt-2 text-center">
              Press Enter to send • Ask about policies, procedures, or documentation
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ConversationAgent;
