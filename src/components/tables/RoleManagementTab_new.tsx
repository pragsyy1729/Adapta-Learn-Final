import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Pencil, Trash2, Eye, Plus, X, Users, Briefcase } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface SkillRequirement {
  skill_name: string;
  required_level: number;
  importance: number;
  category: string;
  description?: string;
  assessment_required?: boolean;
}

interface RoleProfile {
  role_id: string;
  role_name: string;
  department: string;
  level: string;
  skills: SkillRequirement[];
  description?: string;
  responsibilities?: string[];
  min_experience_years?: number;
  preferred_experience_years?: number;
  created_at?: string;
  updated_at?: string;
}

interface RoleSummary {
  role_id: string;
  role_name: string;
  department: string;
  level: string;
  skills_count: number;
}

const emptyRole: Omit<RoleProfile, "role_id" | "created_at" | "updated_at"> = {
  role_name: "",
  department: "",
  level: "",
  skills: [],
  description: "",
  responsibilities: [],
  min_experience_years: 0,
  preferred_experience_years: 0,
};

const emptySkill: Omit<SkillRequirement, "description" | "assessment_required"> = {
  skill_name: "",
  required_level: 3.0,
  importance: 3,
  category: "technical",
};

export default function RoleManagementTab() {
  const { toast } = useToast();
  const [roles, setRoles] = useState<RoleSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState<RoleProfile | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [roleToDelete, setRoleToDelete] = useState<RoleSummary | null>(null);

  // For add/edit dialogs
  const [roleForm, setRoleForm] = useState<Omit<RoleProfile, "role_id" | "created_at" | "updated_at">>(emptyRole);
  const [skillForm, setSkillForm] = useState<Omit<SkillRequirement, "description" | "assessment_required">>(emptySkill);
  const [skillEditIndex, setSkillEditIndex] = useState<number | null>(null);

  // Departments for dropdown
  const departments = [
    "engineering", "data_science", "product", "design", "marketing",
    "sales", "hr", "finance", "operations", "general"
  ];

  // Skill categories
  const skillCategories = [
    "technical", "soft", "domain", "leadership", "communication"
  ];

  useEffect(() => {
    fetchRoles();
  }, []);

  async function fetchRoles() {
    setLoading(true);
    try {
      const res = await fetch("/api/onboarding/roles");
      if (!res.ok) throw new Error("Failed to fetch roles");
      const data = await res.json();
      if (data.success) {
        setRoles(data.data);
      } else {
        throw new Error(data.error || "Failed to fetch roles");
      }
    } catch (error) {
      console.error("Error fetching roles:", error);
      toast({
        title: "Error",
        description: "Failed to load roles. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  async function fetchRoleDetails(roleId: string): Promise<RoleProfile | null> {
    try {
      const res = await fetch(`/api/onboarding/roles/${roleId}`);
      if (!res.ok) throw new Error("Failed to fetch role details");
      const data = await res.json();
      if (data.success) {
        return data.data;
      } else {
        throw new Error(data.error || "Failed to fetch role details");
      }
    } catch (error) {
      console.error("Error fetching role details:", error);
      toast({
        title: "Error",
        description: "Failed to load role details. Please try again.",
        variant: "destructive",
      });
      return null;
    }
  }

  function openAddDialog() {
    setRoleForm(emptyRole);
    setAddDialogOpen(true);
    setSkillForm(emptySkill);
    setSkillEditIndex(null);
  }

  async function openEditDialog(role: RoleSummary) {
    const roleDetails = await fetchRoleDetails(role.role_id);
    if (roleDetails) {
      setSelectedRole(roleDetails);
      setRoleForm({
        role_name: roleDetails.role_name,
        department: roleDetails.department,
        level: roleDetails.level,
        skills: [...roleDetails.skills],
        description: roleDetails.description || "",
        responsibilities: roleDetails.responsibilities || [],
        min_experience_years: roleDetails.min_experience_years || 0,
        preferred_experience_years: roleDetails.preferred_experience_years || 0,
      });
      setEditDialogOpen(true);
      setSkillForm(emptySkill);
      setSkillEditIndex(null);
    }
  }

  async function openViewDialog(role: RoleSummary) {
    const roleDetails = await fetchRoleDetails(role.role_id);
    if (roleDetails) {
      setSelectedRole(roleDetails);
      setViewDialogOpen(true);
    }
  }

  function openDeleteDialog(role: RoleSummary) {
    setRoleToDelete(role);
    setDeleteDialogOpen(true);
  }

  function handleRoleFormChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = e.target;
    setRoleForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSkillFormChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setSkillForm((prev) => ({
      ...prev,
      [name]: name === "required_level" || name === "importance" ? Number(value) : value
    }));
  }

  function addSkillToForm() {
    if (!skillForm.skill_name.trim()) return;
    setRoleForm((prev) => ({ ...prev, skills: [...prev.skills, { ...skillForm, description: "", assessment_required: false }] }));
    setSkillForm(emptySkill);
    setSkillEditIndex(null);
  }

  function editSkillInForm() {
    if (skillEditIndex === null) return;
    setRoleForm((prev) => ({
      ...prev,
      skills: prev.skills.map((s, i) => (i === skillEditIndex ? { ...skillForm, description: s.description || "", assessment_required: s.assessment_required || false } : s)),
    }));
    setSkillForm(emptySkill);
    setSkillEditIndex(null);
  }

  function removeSkillFromForm(idx: number) {
    setRoleForm((prev) => ({ ...prev, skills: prev.skills.filter((_, i) => i !== idx) }));
    setSkillForm(emptySkill);
    setSkillEditIndex(null);
  }

  function startEditSkill(idx: number) {
    const skill = roleForm.skills[idx];
    setSkillForm({
      skill_name: skill.skill_name,
      required_level: skill.required_level,
      importance: skill.importance,
      category: skill.category,
    });
    setSkillEditIndex(idx);
  }

  async function handleAddRole() {
    try {
      const res = await fetch("/api/onboarding/roles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(roleForm),
      });

      if (res.ok) {
        toast({
          title: "Success",
          description: "Role created successfully!",
        });
        fetchRoles();
        setAddDialogOpen(false);
      } else {
        const error = await res.json();
        throw new Error(error.error || "Failed to create role");
      }
    } catch (error) {
      console.error("Error creating role:", error);
      toast({
        title: "Error",
        description: "Failed to create role. Please try again.",
        variant: "destructive",
      });
    }
  }

  async function handleEditRole() {
    if (!selectedRole) return;
    try {
      const res = await fetch(`/api/onboarding/roles/${selectedRole.role_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(roleForm),
      });

      if (res.ok) {
        toast({
          title: "Success",
          description: "Role updated successfully!",
        });
        fetchRoles();
        setEditDialogOpen(false);
      } else {
        const error = await res.json();
        throw new Error(error.error || "Failed to update role");
      }
    } catch (error) {
      console.error("Error updating role:", error);
      toast({
        title: "Error",
        description: "Failed to update role. Please try again.",
        variant: "destructive",
      });
    }
  }

  async function handleDeleteRole() {
    if (!roleToDelete) return;
    try {
      const res = await fetch(`/api/onboarding/roles/${roleToDelete.role_id}`, {
        method: "DELETE"
      });

      if (res.ok) {
        toast({
          title: "Success",
          description: "Role deleted successfully!",
        });
        fetchRoles();
        setDeleteDialogOpen(false);
      } else {
        const error = await res.json();
        throw new Error(error.error || "Failed to delete role");
      }
    } catch (error) {
      console.error("Error deleting role:", error);
      toast({
        title: "Error",
        description: "Failed to delete role. Please try again.",
        variant: "destructive",
      });
    }
  }

  function getLevelBadgeColor(level: string) {
    switch (level.toLowerCase()) {
      case "junior": return "bg-green-100 text-green-800";
      case "mid": return "bg-blue-100 text-blue-800";
      case "senior": return "bg-purple-100 text-purple-800";
      case "lead": return "bg-orange-100 text-orange-800";
      default: return "bg-gray-100 text-gray-800";
    }
  }

  function getCategoryBadgeColor(category: string) {
    switch (category.toLowerCase()) {
      case "technical": return "bg-blue-100 text-blue-800";
      case "soft": return "bg-green-100 text-green-800";
      case "domain": return "bg-purple-100 text-purple-800";
      case "leadership": return "bg-orange-100 text-orange-800";
      case "communication": return "bg-pink-100 text-pink-800";
      default: return "bg-gray-100 text-gray-800";
    }
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">Role Management</h2>
          <p className="text-muted-foreground">Manage roles and their required skills for onboarding</p>
        </div>
        <Button onClick={openAddDialog} size="sm" className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Role
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading roles...</div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Role Name</TableHead>
              <TableHead>Department</TableHead>
              <TableHead>Level</TableHead>
              <TableHead>Skills</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {roles.map((role) => (
              <TableRow key={role.role_id}>
                <TableCell className="font-medium">{role.role_name}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="capitalize">
                    {role.department.replace('_', ' ')}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge className={getLevelBadgeColor(role.level)}>
                    {role.level}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-muted-foreground" />
                    <span>{role.skills_count} skills</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon" onClick={() => openViewDialog(role)}>
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => openEditDialog(role)}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => openDeleteDialog(role)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {/* Add Role Dialog */}
      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Add New Role
            </DialogTitle>
            <DialogDescription>
              Create a new role with required skills and competencies
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="role_name">Role Name *</Label>
                <Input
                  id="role_name"
                  name="role_name"
                  value={roleForm.role_name}
                  onChange={handleRoleFormChange}
                  placeholder="e.g., Senior Software Engineer"
                />
              </div>
              <div>
                <Label htmlFor="department">Department *</Label>
                <Select value={roleForm.department} onValueChange={(value) => setRoleForm(prev => ({ ...prev, department: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map(dep => (
                      <SelectItem key={dep} value={dep} className="capitalize">
                        {dep.replace('_', ' ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="level">Level *</Label>
                <Select value={roleForm.level} onValueChange={(value) => setRoleForm(prev => ({ ...prev, level: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="junior">Junior</SelectItem>
                    <SelectItem value="mid">Mid</SelectItem>
                    <SelectItem value="senior">Senior</SelectItem>
                    <SelectItem value="lead">Lead</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="min_experience_years">Min Experience (years)</Label>
                <Input
                  id="min_experience_years"
                  name="min_experience_years"
                  type="number"
                  min="0"
                  value={roleForm.min_experience_years}
                  onChange={handleRoleFormChange}
                />
              </div>
              <div>
                <Label htmlFor="preferred_experience_years">Preferred Experience (years)</Label>
                <Input
                  id="preferred_experience_years"
                  name="preferred_experience_years"
                  type="number"
                  min="0"
                  value={roleForm.preferred_experience_years}
                  onChange={handleRoleFormChange}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                name="description"
                value={roleForm.description}
                onChange={handleRoleFormChange}
                placeholder="Brief description of the role"
              />
            </div>

            <Separator />

            {/* Skills Management */}
            <div>
              <Label className="text-base font-semibold">Required Skills</Label>
              <div className="mt-4 space-y-3">
                {roleForm.skills.map((skill, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">{skill.skill_name}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={getCategoryBadgeColor(skill.category)}>
                          {skill.category}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          Level: {skill.required_level}/5 • Importance: {skill.importance}/5
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => startEditSkill(idx)}>
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => removeSkillFromForm(idx)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}

                {/* Add/Edit Skill Form */}
                <div className="p-4 border-2 border-dashed border-muted-foreground/25 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <Label htmlFor="skill_name">Skill Name *</Label>
                      <Input
                        id="skill_name"
                        name="skill_name"
                        value={skillForm.skill_name}
                        onChange={handleSkillFormChange}
                        placeholder="e.g., Python, React, Leadership"
                      />
                    </div>
                    <div>
                      <Label htmlFor="category">Category</Label>
                      <Select value={skillForm.category} onValueChange={(value) => setSkillForm(prev => ({ ...prev, category: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          {skillCategories.map(cat => (
                            <SelectItem key={cat} value={cat} className="capitalize">
                              {cat.replace('_', ' ')}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <Label htmlFor="required_level">Required Level (1-5)</Label>
                      <Input
                        id="required_level"
                        name="required_level"
                        type="number"
                        min="1"
                        max="5"
                        value={skillForm.required_level}
                        onChange={handleSkillFormChange}
                      />
                    </div>
                    <div>
                      <Label htmlFor="importance">Importance (1-5)</Label>
                      <Input
                        id="importance"
                        name="importance"
                        type="number"
                        min="1"
                        max="5"
                        value={skillForm.importance}
                        onChange={handleSkillFormChange}
                      />
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {skillEditIndex === null ? (
                      <Button size="sm" onClick={addSkillToForm} disabled={!skillForm.skill_name.trim()}>
                        <Plus className="w-4 h-4 mr-2" />
                        Add Skill
                      </Button>
                    ) : (
                      <Button size="sm" onClick={editSkillInForm}>
                        Update Skill
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSkillForm(emptySkill);
                        setSkillEditIndex(null);
                      }}
                    >
                      <X className="w-4 h-4 mr-2" />
                      Clear
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleAddRole}
              disabled={!roleForm.role_name || !roleForm.department || !roleForm.level}
            >
              Create Role
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Role Dialog - Similar to Add but pre-populated */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Pencil className="w-5 h-5" />
              Edit Role
            </DialogTitle>
            <DialogDescription>
              Update role information and required skills
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_role_name">Role Name *</Label>
                <Input
                  id="edit_role_name"
                  name="role_name"
                  value={roleForm.role_name}
                  onChange={handleRoleFormChange}
                  placeholder="e.g., Senior Software Engineer"
                />
              </div>
              <div>
                <Label htmlFor="edit_department">Department *</Label>
                <Select value={roleForm.department} onValueChange={(value) => setRoleForm(prev => ({ ...prev, department: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map(dep => (
                      <SelectItem key={dep} value={dep} className="capitalize">
                        {dep.replace('_', ' ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="edit_level">Level *</Label>
                <Select value={roleForm.level} onValueChange={(value) => setRoleForm(prev => ({ ...prev, level: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="junior">Junior</SelectItem>
                    <SelectItem value="mid">Mid</SelectItem>
                    <SelectItem value="senior">Senior</SelectItem>
                    <SelectItem value="lead">Lead</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit_min_exp">Min Experience (years)</Label>
                <Input
                  id="edit_min_exp"
                  name="min_experience_years"
                  type="number"
                  min="0"
                  value={roleForm.min_experience_years}
                  onChange={handleRoleFormChange}
                />
              </div>
              <div>
                <Label htmlFor="edit_pref_exp">Preferred Experience (years)</Label>
                <Input
                  id="edit_pref_exp"
                  name="preferred_experience_years"
                  type="number"
                  min="0"
                  value={roleForm.preferred_experience_years}
                  onChange={handleRoleFormChange}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="edit_description">Description</Label>
              <Input
                id="edit_description"
                name="description"
                value={roleForm.description}
                onChange={handleRoleFormChange}
                placeholder="Brief description of the role"
              />
            </div>

            <Separator />

            {/* Skills Management - Same as Add Dialog */}
            <div>
              <Label className="text-base font-semibold">Required Skills</Label>
              <div className="mt-4 space-y-3">
                {roleForm.skills.map((skill, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">{skill.skill_name}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={getCategoryBadgeColor(skill.category)}>
                          {skill.category}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          Level: {skill.required_level}/5 • Importance: {skill.importance}/5
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => startEditSkill(idx)}>
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => removeSkillFromForm(idx)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}

                {/* Add/Edit Skill Form */}
                <div className="p-4 border-2 border-dashed border-muted-foreground/25 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <Label htmlFor="edit_skill_name">Skill Name *</Label>
                      <Input
                        id="edit_skill_name"
                        name="skill_name"
                        value={skillForm.skill_name}
                        onChange={handleSkillFormChange}
                        placeholder="e.g., Python, React, Leadership"
                      />
                    </div>
                    <div>
                      <Label htmlFor="edit_category">Category</Label>
                      <Select value={skillForm.category} onValueChange={(value) => setSkillForm(prev => ({ ...prev, category: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          {skillCategories.map(cat => (
                            <SelectItem key={cat} value={cat} className="capitalize">
                              {cat.replace('_', ' ')}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <Label htmlFor="edit_required_level">Required Level (1-5)</Label>
                      <Input
                        id="edit_required_level"
                        name="required_level"
                        type="number"
                        min="1"
                        max="5"
                        value={skillForm.required_level}
                        onChange={handleSkillFormChange}
                      />
                    </div>
                    <div>
                      <Label htmlFor="edit_importance">Importance (1-5)</Label>
                      <Input
                        id="edit_importance"
                        name="importance"
                        type="number"
                        min="1"
                        max="5"
                        value={skillForm.importance}
                        onChange={handleSkillFormChange}
                      />
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {skillEditIndex === null ? (
                      <Button size="sm" onClick={addSkillToForm} disabled={!skillForm.skill_name.trim()}>
                        <Plus className="w-4 h-4 mr-2" />
                        Add Skill
                      </Button>
                    ) : (
                      <Button size="sm" onClick={editSkillInForm}>
                        Update Skill
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSkillForm(emptySkill);
                        setSkillEditIndex(null);
                      }}
                    >
                      <X className="w-4 h-4 mr-2" />
                      Clear
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleEditRole}
              disabled={!roleForm.role_name || !roleForm.department || !roleForm.level}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Role Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Role Details
            </DialogTitle>
          </DialogHeader>

          {selectedRole && (
            <div className="space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <Label className="text-sm font-semibold">Role Name</Label>
                  <p className="text-lg font-medium">{selectedRole.role_name}</p>
                </div>
                <div>
                  <Label className="text-sm font-semibold">Department</Label>
                  <Badge variant="outline" className="capitalize">
                    {selectedRole.department.replace('_', ' ')}
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-6">
                <div>
                  <Label className="text-sm font-semibold">Level</Label>
                  <Badge className={getLevelBadgeColor(selectedRole.level)}>
                    {selectedRole.level}
                  </Badge>
                </div>
                <div>
                  <Label className="text-sm font-semibold">Min Experience</Label>
                  <p>{selectedRole.min_experience_years || 0} years</p>
                </div>
                <div>
                  <Label className="text-sm font-semibold">Preferred Experience</Label>
                  <p>{selectedRole.preferred_experience_years || 0} years</p>
                </div>
              </div>

              {selectedRole.description && (
                <div>
                  <Label className="text-sm font-semibold">Description</Label>
                  <p className="text-muted-foreground">{selectedRole.description}</p>
                </div>
              )}

              {/* Skills */}
              <div>
                <Label className="text-sm font-semibold">Required Skills ({selectedRole.skills.length})</Label>
                <div className="mt-3 space-y-3">
                  {selectedRole.skills.map((skill, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="font-medium">{skill.skill_name}</div>
                        <div className="flex items-center gap-3 mt-2">
                          <Badge className={getCategoryBadgeColor(skill.category)}>
                            {skill.category}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            Required Level: {skill.required_level}/5
                          </span>
                          <span className="text-sm text-muted-foreground">
                            Importance: {skill.importance}/5
                          </span>
                        </div>
                        {skill.description && (
                          <p className="text-sm text-muted-foreground mt-1">{skill.description}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Responsibilities */}
              {selectedRole.responsibilities && selectedRole.responsibilities.length > 0 && (
                <div>
                  <Label className="text-sm font-semibold">Key Responsibilities</Label>
                  <ul className="mt-2 space-y-1">
                    {selectedRole.responsibilities.map((resp, idx) => (
                      <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        {resp}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Role Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <Trash2 className="w-5 h-5" />
              Delete Role
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the role "{roleToDelete?.role_name}"?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          {roleToDelete && (
            <div className="py-4">
              <div className="bg-muted p-4 rounded-lg">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Role:</span> {roleToDelete.role_name}
                  </div>
                  <div>
                    <span className="font-medium">Department:</span> {roleToDelete.department}
                  </div>
                  <div>
                    <span className="font-medium">Level:</span> {roleToDelete.level}
                  </div>
                  <div>
                    <span className="font-medium">Skills:</span> {roleToDelete.skills_count}
                  </div>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteRole}>
              Delete Role
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
