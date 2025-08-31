import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  Bell,
  AlertTriangle,
  Users,
  CheckCircle,
  XCircle,
  Clock,
  TrendingDown
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface GroupInvite {
  id: string;
  group_id: string;
  group_name: string;
  invited_by: string;
  invited_user: string;
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
}

interface LearningProgressWarning {
  type: 'slow_progress' | 'stalled_learning' | 'no_progress';
  message: string;
  learning_path_id?: string;
  learning_path_name?: string;
  days_since_last_access?: number;
  progress_percent?: number;
}

interface NotificationsProps {
  userId: string;
}

const Notifications: React.FC<NotificationsProps> = ({ userId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [groupInvites, setGroupInvites] = useState<GroupInvite[]>([]);
  const [learningWarnings, setLearningWarnings] = useState<LearningProgressWarning[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const fetchNotifications = async () => {
    if (!userId) return;

    setLoading(true);
    try {
      // Fetch group invites
      const invitesRes = await fetch(`/api/groups/invites/${userId}`);
      if (invitesRes.ok) {
        const invites = await invitesRes.json();
        setGroupInvites(invites);
      }

      // Fetch learning progress warnings
      const warningsRes = await fetch(`/api/learning-warnings/${userId}`);
      if (warningsRes.ok) {
        const warnings = await warningsRes.json();
        setLearningWarnings(warnings);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [userId]);

  const handleInviteResponse = async (inviteId: string, accept: boolean) => {
    try {
      const response = await fetch(`/api/groups/invites/${inviteId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ accept })
      });

      if (response.ok) {
        // Remove the invite from the list
        setGroupInvites(prev => prev.filter(invite => invite.id !== inviteId));

        toast({
          title: accept ? "Group invite accepted!" : "Group invite declined",
          description: accept
            ? "You have successfully joined the group."
            : "The group invite has been declined.",
        });

        // Refresh notifications
        fetchNotifications();
      }
    } catch (error) {
      console.error('Error responding to invite:', error);
      toast({
        title: "Error",
        description: "Failed to respond to group invite.",
        variant: "destructive",
      });
    }
  };

  const totalNotifications = groupInvites.length + learningWarnings.length;

  const getWarningIcon = (type: string) => {
    switch (type) {
      case 'slow_progress':
        return <TrendingDown className="w-4 h-4 text-orange-500" />;
      case 'stalled_learning':
        return <Clock className="w-4 h-4 text-red-500" />;
      case 'no_progress':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'good_progress':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getWarningColor = (type: string) => {
    switch (type) {
      case 'slow_progress':
        return 'border-orange-200 bg-orange-50';
      case 'stalled_learning':
        return 'border-red-200 bg-red-50';
      case 'no_progress':
        return 'border-yellow-200 bg-yellow-50';
      case 'good_progress':
        return 'border-green-200 bg-green-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  if (!userId) return null;

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        className="relative"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Bell className="w-5 h-5" />
        {totalNotifications > 0 && (
          <Badge
            variant="destructive"
            className="absolute -top-1 -right-1 w-5 h-5 p-0 flex items-center justify-center text-xs"
          >
            {totalNotifications > 9 ? '9+' : totalNotifications}
          </Badge>
        )}
      </Button>

      {isOpen && (
        <Card className="absolute right-0 top-12 w-96 max-h-96 overflow-y-auto shadow-lg border z-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground">Notifications</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
              >
                ✕
              </Button>
            </div>

            {loading ? (
              <div className="text-center py-4 text-muted-foreground">
                Loading notifications...
              </div>
            ) : totalNotifications === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No new notifications</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Group Invites */}
                {groupInvites.map((invite) => (
                  <div key={invite.id} className="border rounded-lg p-3 bg-blue-50 border-blue-200">
                    <div className="flex items-start gap-3">
                      <Users className="w-5 h-5 text-blue-600 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-2">
                          <p className="text-sm font-medium text-foreground">
                            Group Invitation
                          </p>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 hover:bg-blue-100"
                            onClick={() => {
                              // Remove this notification from the list
                              setGroupInvites(prev => prev.filter(inv => inv.id !== invite.id));
                              toast({
                                title: "Notification dismissed",
                                description: "Group invitation notification has been closed.",
                              });
                            }}
                          >
                            <XCircle className="w-3 h-3 text-blue-600" />
                          </Button>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          <strong>{invite.invited_by}</strong> invited you to join <strong>{invite.group_name}</strong>
                        </p>
                        <p className="text-xs text-muted-foreground mb-3">
                          {new Date(invite.created_at).toLocaleDateString()}
                        </p>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleInviteResponse(invite.id, true)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Accept
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleInviteResponse(invite.id, false)}
                            className="border-red-300 text-red-700 hover:bg-red-50"
                          >
                            <XCircle className="w-3 h-3 mr-1" />
                            Decline
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Learning Progress Warnings */}
                {learningWarnings.map((warning, index) => (
                  <div key={index} className={`border rounded-lg p-3 ${getWarningColor(warning.type)}`}>
                    <div className="flex items-start gap-3">
                      {getWarningIcon(warning.type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-2">
                          <p className="text-sm font-medium text-foreground">
                            Learning Progress Alert
                          </p>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 hover:bg-gray-100"
                            onClick={() => {
                              // Remove this warning from the list
                              setLearningWarnings(prev => prev.filter((_, i) => i !== index));
                              toast({
                                title: "Notification dismissed",
                                description: "Learning progress alert has been closed.",
                              });
                            }}
                          >
                            <XCircle className="w-3 h-3 text-gray-600" />
                          </Button>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {warning.message}
                        </p>
                        {warning.learning_path_name && (
                          <p className="text-xs text-muted-foreground">
                            Learning Path: {warning.learning_path_name}
                          </p>
                        )}
                        {warning.days_since_last_access && (
                          <p className="text-xs text-muted-foreground">
                            Last accessed: {warning.days_since_last_access} days ago
                          </p>
                        )}
                        {warning.progress_percent !== undefined && (
                          <p className="text-xs text-muted-foreground">
                            Current progress: {warning.progress_percent}%
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {totalNotifications > 0 && (
                  <>
                    <Separator />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={fetchNotifications}
                      className="w-full"
                    >
                      Refresh Notifications
                    </Button>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Notifications;
