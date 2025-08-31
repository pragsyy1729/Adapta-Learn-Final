import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  Users,
  Calendar,
  UserPlus,
  Mail,
  Phone,
  MapPin,
  Award,
  Clock,
  CheckCircle,
  XCircle,
  Plus,
  Send,
  UserCheck,
  Loader2,
  RefreshCw
} from "lucide-react";
import { useSessionTracking } from "@/hooks/useSessionTracking";

interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location?: string;
  organizer: string;
  attendees: string[];
  type: 'meeting' | 'training' | 'social' | 'other';
}

interface Group {
  id: string;
  name: string;
  description: string;
  created_by: string;
  members: string[];
  pending_invites: string[];
  created_at: string;
  category: string;
}

interface GroupInvite {
  id: string;
  group_id: string;
  group_name: string;
  invited_by: string;
  invited_user: string;
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
}

const DashboardCollaborationTab = () => {
  const [activeTab, setActiveTab] = useState("events");
  const [events, setEvents] = useState<Event[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [invites, setInvites] = useState<GroupInvite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Group creation state
  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupDescription, setNewGroupDescription] = useState("");
  const [newGroupCategory, setNewGroupCategory] = useState("");
  const [inviteEmails, setInviteEmails] = useState("");

  // Get user from localStorage
  const [user, setUser] = useState<any>(null);
  const userId = user?.user_id || '';
  const { trackActivity } = useSessionTracking(userId);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const fetchCollaborationData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");

      // Fetch events
      const eventsRes = await fetch('/api/events');
      if (eventsRes.ok) {
        const eventsData = await eventsRes.json();
        setEvents(eventsData || []);
      }

      // Fetch groups
      const groupsRes = await fetch('/api/groups');
      if (groupsRes.ok) {
        const groupsData = await groupsRes.json();
        setGroups(groupsData || []);
      }

      // Fetch invites for current user
      if (userId) {
        const invitesRes = await fetch(`/api/groups/invites/${userId}`);
        if (invitesRes.ok) {
          const invitesData = await invitesRes.json();
          setInvites(invitesData || []);
        }
      }

      setError(null);
    } catch (error) {
      console.error('Error fetching collaboration data:', error);
      setError("Failed to load collaboration data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollaborationData();
    trackActivity('collaboration_view');
  }, [userId]);

  const createGroup = async () => {
    if (!newGroupName.trim()) return;

    try {
      const token = localStorage.getItem("token");
      const response = await fetch('/api/groups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          name: newGroupName,
          description: newGroupDescription,
          category: newGroupCategory,
          created_by: userId,
          invite_emails: inviteEmails.split(',').map(email => email.trim()).filter(email => email)
        })
      });

      if (response.ok) {
        setNewGroupName("");
        setNewGroupDescription("");
        setNewGroupCategory("");
        setInviteEmails("");
        fetchCollaborationData(); // Refresh data
        trackActivity('group_created');
      } else {
        setError("Failed to create group");
      }
    } catch (error) {
      setError("Network error creating group");
    }
  };

  const handleInviteResponse = async (inviteId: string, accept: boolean) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/api/groups/invites/${inviteId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ accept })
      });

      if (response.ok) {
        fetchCollaborationData(); // Refresh data
        trackActivity(accept ? 'group_invite_accepted' : 'group_invite_declined');
      }
    } catch (error) {
      setError("Failed to respond to invite");
    }
  };

  const getRoleIcon = (role: string | undefined) => {
    if (!role) return Users;
    if (role.toLowerCase().includes('manager')) return Crown;
    if (role.toLowerCase().includes('admin')) return Award;
    if (role.toLowerCase().includes('director')) return Award;
    return Users;
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'meeting': return 'bg-blue-100 text-blue-800';
      case 'training': return 'bg-green-100 text-green-800';
      case 'social': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getGroupCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'technical': return 'bg-blue-100 text-blue-800';
      case 'project': return 'bg-green-100 text-green-800';
      case 'department': return 'bg-purple-100 text-purple-800';
      case 'learning': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Loading Collaboration Hub</h3>
          <p className="text-muted-foreground">Fetching team data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Users className="w-8 h-8 text-primary" />
          <h2 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            Collaboration Hub
          </h2>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Connect with your team, stay updated on events, and collaborate in groups
        </p>
        <div className="flex items-center justify-center gap-4 mt-4">
          <Badge variant="outline" className="text-xs">
            {groups.length} Groups
          </Badge>
          <Badge variant="outline" className="text-xs">
            {events.length} Upcoming Events
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchCollaborationData}
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <RefreshCw className="w-4 h-4 mr-2" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-700">
            <XCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </Card>
      )}

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="events" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Events
          </TabsTrigger>
          <TabsTrigger value="groups" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Groups
          </TabsTrigger>
        </TabsList>

        {/* Events Tab */}
        <TabsContent value="events" className="space-y-6">
          <Card className="shadow-card hover:shadow-elegant transition-smooth">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Calendar className="w-6 h-6 text-primary" />
                <CardTitle>Upcoming Events</CardTitle>
              </div>
              <CardDescription>
                Stay updated on team meetings, training sessions, and company events
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {events.map((event) => (
                  <Card key={event.id} className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-foreground">{event.title}</h3>
                          <Badge className={getEventTypeColor(event.type)}>
                            {event.type}
                          </Badge>
                        </div>
                        <p className="text-muted-foreground mb-3">{event.description}</p>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-primary" />
                            <span>{new Date(event.date).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-primary" />
                            <span>{event.time}</span>
                          </div>
                          {event.location && (
                            <div className="flex items-center gap-2">
                              <MapPin className="w-4 h-4 text-primary" />
                              <span>{event.location}</span>
                            </div>
                          )}
                          <div className="flex items-center gap-2">
                            <Users className="w-4 h-4 text-primary" />
                            <span>{event.attendees.length} attendees</span>
                          </div>
                        </div>

                        <div className="mt-3">
                          <span className="text-sm text-muted-foreground">Organized by: </span>
                          <span className="text-sm font-medium">{event.organizer}</span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {events.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No upcoming events</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Groups Tab */}
        <TabsContent value="groups" className="space-y-6">
          {/* Pending Invites */}
          {invites.length > 0 && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-blue-900">Pending Group Invites</CardTitle>
                <CardDescription className="text-blue-700">
                  You have {invites.length} pending group invitation{invites.length > 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {invites.map((invite) => (
                    <div key={invite.id} className="flex items-center justify-between p-4 bg-white rounded-lg border">
                      <div>
                        <h4 className="font-medium text-foreground">{invite.group_name}</h4>
                        <p className="text-sm text-muted-foreground">
                          Invited by {invite.invited_by} • {new Date(invite.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleInviteResponse(invite.id, true)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Accept
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleInviteResponse(invite.id, false)}
                          className="border-red-300 text-red-700 hover:bg-red-50"
                        >
                          <XCircle className="w-4 h-4 mr-1" />
                          Decline
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Create Group */}
          <Card className="shadow-card hover:shadow-elegant transition-smooth">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Plus className="w-6 h-6 text-primary" />
                <CardTitle>Create New Group</CardTitle>
              </div>
              <CardDescription>
                Start a new collaboration group and invite team members
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="group-name">Group Name</Label>
                    <Input
                      id="group-name"
                      value={newGroupName}
                      onChange={(e) => setNewGroupName(e.target.value)}
                      placeholder="Enter group name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="group-category">Category</Label>
                    <Select value={newGroupCategory} onValueChange={setNewGroupCategory}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="technical">Technical</SelectItem>
                        <SelectItem value="project">Project</SelectItem>
                        <SelectItem value="department">Department</SelectItem>
                        <SelectItem value="learning">Learning</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="group-description">Description</Label>
                  <Textarea
                    id="group-description"
                    value={newGroupDescription}
                    onChange={(e) => setNewGroupDescription(e.target.value)}
                    placeholder="Describe the purpose of this group"
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="invite-emails">Invite Members (comma-separated emails)</Label>
                  <Textarea
                    id="invite-emails"
                    value={inviteEmails}
                    onChange={(e) => setInviteEmails(e.target.value)}
                    placeholder="user1@company.com, user2@company.com"
                    rows={2}
                  />
                </div>

                <Button
                  onClick={createGroup}
                  disabled={!newGroupName.trim()}
                  className="w-full"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Create Group & Send Invites
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Existing Groups */}
          <Card className="shadow-card hover:shadow-elegant transition-smooth">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Users className="w-6 h-6 text-primary" />
                <CardTitle>Your Groups</CardTitle>
              </div>
              <CardDescription>
                Groups you're a member of
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {groups.map((group) => (
                  <Card key={group.id} className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-foreground">{group.name}</h3>
                          <Badge className={getGroupCategoryColor(group.category)}>
                            {group.category}
                          </Badge>
                        </div>
                        <p className="text-muted-foreground mb-3">{group.description}</p>

                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{group.members.length} members</span>
                          <span>{group.pending_invites.length} pending invites</span>
                          <span>Created {new Date(group.created_at).toLocaleDateString()}</span>
                        </div>

                        <div className="mt-3">
                          <span className="text-sm text-muted-foreground">Created by: </span>
                          <span className="text-sm font-medium">{group.created_by}</span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Send className="w-4 h-4 mr-1" />
                          Invite
                        </Button>
                        <Button size="sm" variant="outline">
                          <Users className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {groups.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>You haven't joined any groups yet</p>
                  <p className="text-sm mt-2">Create a group above to get started!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DashboardCollaborationTab;
