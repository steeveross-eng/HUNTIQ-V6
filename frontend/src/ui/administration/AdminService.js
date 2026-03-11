/**
 * AdminService - V5-ULTIME Administration Premium
 * ================================================
 * 
 * Service centralisé pour les appels API d'administration.
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export const AdminService = {
  // ============ DASHBOARD ============
  async getDashboard() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/admin/dashboard`);
      if (!response.ok) throw new Error('Failed to fetch dashboard');
      return await response.json();
    } catch (error) {
      console.error('AdminService.getDashboard error:', error);
      return { success: false, error: error.message };
    }
  },

  // ============ PAYMENTS ============
  async getTransactions(limit = 50, status = null, skip = 0) {
    const params = new URLSearchParams({ limit, skip });
    if (status) params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/payments/transactions?${params}`);
    return await response.json();
  },

  async getRevenueStats(days = 30) {
    const response = await fetch(`${API_BASE}/api/v1/admin/payments/revenue?days=${days}`);
    return await response.json();
  },

  async getSubscriptions(tier = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (tier) params.append('tier', tier);
    const response = await fetch(`${API_BASE}/api/v1/admin/payments/subscriptions?${params}`);
    return await response.json();
  },

  // ============ FREEMIUM ============
  async getQuotaOverview() {
    const response = await fetch(`${API_BASE}/api/v1/admin/freemium/quotas`);
    return await response.json();
  },

  async getUserFreemiumStatus(userId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/freemium/users/${userId}`);
    return await response.json();
  },

  async setUserOverride(userId, overrides) {
    const response = await fetch(`${API_BASE}/api/v1/admin/freemium/users/${userId}/override`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(overrides)
    });
    return await response.json();
  },

  async getTierDistribution() {
    const response = await fetch(`${API_BASE}/api/v1/admin/freemium/tiers/stats`);
    return await response.json();
  },

  // ============ UPSELL ============
  async getUpsellCampaigns() {
    const response = await fetch(`${API_BASE}/api/v1/admin/upsell/campaigns`);
    return await response.json();
  },

  async toggleCampaign(campaignName, enabled) {
    const response = await fetch(
      `${API_BASE}/api/v1/admin/upsell/campaigns/${campaignName}/toggle?enabled=${enabled}`,
      { method: 'PUT' }
    );
    return await response.json();
  },

  async getUpsellAnalytics(days = 30) {
    const response = await fetch(`${API_BASE}/api/v1/admin/upsell/analytics?days=${days}`);
    return await response.json();
  },

  // ============ ONBOARDING ============
  async getOnboardingStats() {
    const response = await fetch(`${API_BASE}/api/v1/admin/onboarding/stats`);
    return await response.json();
  },

  async getOnboardingFlows() {
    const response = await fetch(`${API_BASE}/api/v1/admin/onboarding/flows`);
    return await response.json();
  },

  // ============ TUTORIALS ============
  async getTutorials() {
    const response = await fetch(`${API_BASE}/api/v1/admin/tutorials/list`);
    return await response.json();
  },

  async toggleTutorial(tutorialId, enabled) {
    const response = await fetch(
      `${API_BASE}/api/v1/admin/tutorials/${tutorialId}/toggle?enabled=${enabled}`,
      { method: 'PUT' }
    );
    return await response.json();
  },

  // ============ RULES ============
  async getRules() {
    const response = await fetch(`${API_BASE}/api/v1/admin/rules/list`);
    return await response.json();
  },

  async toggleRule(ruleId, enabled) {
    const response = await fetch(
      `${API_BASE}/api/v1/admin/rules/${ruleId}/toggle?enabled=${enabled}`,
      { method: 'PUT' }
    );
    return await response.json();
  },

  async updateRuleWeight(ruleId, weight) {
    const response = await fetch(
      `${API_BASE}/api/v1/admin/rules/${ruleId}/weight?weight=${weight}`,
      { method: 'PUT' }
    );
    return await response.json();
  },

  // ============ STRATEGY ============
  async getStrategies(limit = 50, userId = null) {
    const params = new URLSearchParams({ limit });
    if (userId) params.append('user_id', userId);
    const response = await fetch(`${API_BASE}/api/v1/admin/strategy/generated?${params}`);
    return await response.json();
  },

  async getStrategyDiagnostics() {
    const response = await fetch(`${API_BASE}/api/v1/admin/strategy/diagnostics`);
    return await response.json();
  },

  // ============ USERS ============
  async getUsers(limit = 50, role = null, tier = null) {
    const params = new URLSearchParams({ limit });
    if (role) params.append('role', role);
    if (tier) params.append('tier', tier);
    const response = await fetch(`${API_BASE}/api/v1/admin/users/list?${params}`);
    return await response.json();
  },

  async getUserDetail(userId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/users/${userId}`);
    return await response.json();
  },

  async updateUserRole(userId, role) {
    const response = await fetch(
      `${API_BASE}/api/v1/admin/users/${userId}/role?role=${role}`,
      { method: 'PUT' }
    );
    return await response.json();
  },

  // ============ LOGS ============
  async getErrorLogs(limit = 100, severity = null) {
    const params = new URLSearchParams({ limit });
    if (severity) params.append('severity', severity);
    const response = await fetch(`${API_BASE}/api/v1/admin/logs/errors?${params}`);
    return await response.json();
  },

  async getWebhookLogs(limit = 100) {
    const response = await fetch(`${API_BASE}/api/v1/admin/logs/webhooks?limit=${limit}`);
    return await response.json();
  },

  async getEventLogs(limit = 100, eventType = null) {
    const params = new URLSearchParams({ limit });
    if (eventType) params.append('event_type', eventType);
    const response = await fetch(`${API_BASE}/api/v1/admin/logs/events?${params}`);
    return await response.json();
  },

  // ============ SETTINGS ============
  async getSettings() {
    const response = await fetch(`${API_BASE}/api/v1/admin/settings`);
    return await response.json();
  },

  async updateSetting(key, value) {
    const response = await fetch(`${API_BASE}/api/v1/admin/settings/${key}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(value)
    });
    return await response.json();
  },

  async getApiKeysStatus() {
    const response = await fetch(`${API_BASE}/api/v1/admin/settings/api-keys`);
    return await response.json();
  },

  async getToggles() {
    const response = await fetch(`${API_BASE}/api/v1/admin/settings/toggles`);
    return await response.json();
  },

  async updateToggle(toggleId, enabled) {
    const response = await fetch(
      `${API_BASE}/api/v1/admin/settings/toggles/${toggleId}?enabled=${enabled}`,
      { method: 'PUT' }
    );
    return await response.json();
  },

  // ============ E-COMMERCE (Phase 1) ============
  async ecommerceGetDashboard() {
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/dashboard`);
    return await response.json();
  },

  async ecommerceGetOrders(limit = 50, status = null) {
    const params = new URLSearchParams({ limit });
    if (status && status !== 'all') params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/orders?${params}`);
    return await response.json();
  },

  async ecommerceUpdateOrderStatus(orderId, status) {
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/orders/${orderId}/status?status=${status}`, { method: 'PUT' });
    return await response.json();
  },

  async ecommerceGetProducts(limit = 50, category = null) {
    const params = new URLSearchParams({ limit });
    if (category) params.append('category', category);
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/products?${params}`);
    return await response.json();
  },

  async ecommerceGetSuppliers(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/suppliers?limit=${limit}`);
    return await response.json();
  },

  async ecommerceGetCustomers(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/customers?limit=${limit}`);
    return await response.json();
  },

  async ecommerceGetCommissions(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/commissions?limit=${limit}`);
    return await response.json();
  },

  async ecommerceGetPerformance() {
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/performance`);
    return await response.json();
  },

  async ecommerceGetAlerts() {
    const response = await fetch(`${API_BASE}/api/v1/admin/ecommerce/alerts`);
    return await response.json();
  },

  // ============ CONTENT (Phase 2) ============
  async contentGetCategories() {
    const response = await fetch(`${API_BASE}/api/v1/admin/content/categories`);
    return await response.json();
  },

  async contentCreateCategory(data) {
    const response = await fetch(`${API_BASE}/api/v1/admin/content/categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await response.json();
  },

  async contentUpdateCategory(categoryId, data) {
    const response = await fetch(`${API_BASE}/api/v1/admin/content/categories/${categoryId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await response.json();
  },

  async contentDeleteCategory(categoryId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/content/categories/${categoryId}`, { method: 'DELETE' });
    return await response.json();
  },

  async contentGetDepotItems(status = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status) params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/content/depot?${params}`);
    return await response.json();
  },

  async contentGetSeoAnalytics() {
    const response = await fetch(`${API_BASE}/api/v1/admin/content/seo-analytics`);
    return await response.json();
  },

  // ============ BACKUP (Phase 2) ============
  async backupGetStats() {
    const response = await fetch(`${API_BASE}/api/v1/admin/backup/stats`);
    return await response.json();
  },

  async backupGetCodeFiles(search = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (search) params.append('search', search);
    const response = await fetch(`${API_BASE}/api/v1/admin/backup/code/files?${params}`);
    return await response.json();
  },

  async backupGetPromptVersions(promptType = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (promptType) params.append('prompt_type', promptType);
    const response = await fetch(`${API_BASE}/api/v1/admin/backup/prompts?${params}`);
    return await response.json();
  },

  async backupGetDbBackups(limit = 20) {
    const response = await fetch(`${API_BASE}/api/v1/admin/backup/database?limit=${limit}`);
    return await response.json();
  },

  async backupCreateDbBackup(backupType = 'manual', description = '') {
    const params = new URLSearchParams({ backup_type: backupType, description });
    const response = await fetch(`${API_BASE}/api/v1/admin/backup/database?${params}`, { method: 'POST' });
    return await response.json();
  },

  // ============ MAINTENANCE (Phase 3) ============
  async maintenanceGetStatus() {
    const response = await fetch(`${API_BASE}/api/v1/admin/maintenance/status`);
    return await response.json();
  },

  async maintenanceToggle(enabled, message = null, estimatedEnd = null) {
    const params = new URLSearchParams({ enabled });
    if (message) params.append('message', message);
    if (estimatedEnd) params.append('estimated_end', estimatedEnd);
    const response = await fetch(`${API_BASE}/api/v1/admin/maintenance/toggle?${params}`, { method: 'PUT' });
    return await response.json();
  },

  async maintenanceGetAccessRules() {
    const response = await fetch(`${API_BASE}/api/v1/admin/maintenance/access-rules`);
    return await response.json();
  },

  async maintenanceGetAllowedIps() {
    const response = await fetch(`${API_BASE}/api/v1/admin/maintenance/allowed-ips`);
    return await response.json();
  },

  async maintenanceGetLogs(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/maintenance/logs?limit=${limit}`);
    return await response.json();
  },

  async maintenanceGetScheduled() {
    const response = await fetch(`${API_BASE}/api/v1/admin/maintenance/scheduled`);
    return await response.json();
  },

  async maintenanceGetSystemStatus() {
    const response = await fetch(`${API_BASE}/api/v1/admin/maintenance/system-status`);
    return await response.json();
  },

  // ============ CONTACTS (Phase 3) ============
  async contactsGetAll(entityType = null, status = null, search = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (entityType) params.append('entity_type', entityType);
    if (status) params.append('status', status);
    if (search) params.append('search', search);
    const response = await fetch(`${API_BASE}/api/v1/admin/contacts?${params}`);
    return await response.json();
  },

  async contactsGetStats() {
    const response = await fetch(`${API_BASE}/api/v1/admin/contacts/stats`);
    return await response.json();
  },

  async contactsGetTags() {
    const response = await fetch(`${API_BASE}/api/v1/admin/contacts/tags`);
    return await response.json();
  },

  async contactsCreate(data) {
    const response = await fetch(`${API_BASE}/api/v1/admin/contacts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await response.json();
  },

  async contactsUpdate(contactId, data) {
    const response = await fetch(`${API_BASE}/api/v1/admin/contacts/${contactId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await response.json();
  },

  async contactsDelete(contactId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/contacts/${contactId}`, { method: 'DELETE' });
    return await response.json();
  },

  // ============ HOTSPOTS (Phase 4) ============
  async hotspotsGetStats() {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/dashboard`);
    return await response.json();
  },

  async hotspotsGetListings(status = 'all', limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status && status !== 'all') params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/listings?${params}`);
    return await response.json();
  },

  async hotspotsGetListingDetail(listingId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/listings/${listingId}`);
    return await response.json();
  },

  async hotspotsUpdateStatus(listingId, status) {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/listings/${listingId}/status?new_status=${status}`, { method: 'PUT' });
    return await response.json();
  },

  async hotspotsToggleFeatured(listingId, isFeatured) {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/listings/${listingId}/featured?is_featured=${isFeatured}`, { method: 'PUT' });
    return await response.json();
  },

  async hotspotsGetOwners(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/owners?limit=${limit}`);
    return await response.json();
  },

  async hotspotsGetRenters(tier = 'all', limit = 50) {
    const params = new URLSearchParams({ limit });
    if (tier && tier !== 'all') params.append('subscription_tier', tier);
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/renters?${params}`);
    return await response.json();
  },

  async hotspotsGetAgreements(status = 'all', limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status && status !== 'all') params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/agreements?${params}`);
    return await response.json();
  },

  async hotspotsGetPricing() {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/pricing`);
    return await response.json();
  },

  async hotspotsUpdatePricing(updates) {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/pricing`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    return await response.json();
  },

  async hotspotsGetRegions() {
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/regions`);
    return await response.json();
  },

  async hotspotsGetPurchases(status = 'all', limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status && status !== 'all') params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/hotspots/purchases?${params}`);
    return await response.json();
  },

  // ============ NETWORKING (Phase 4) ============
  async networkingGetStats() {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/dashboard`);
    return await response.json();
  },

  async networkingGetPosts(visibility = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (visibility) params.append('visibility', visibility);
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/posts?${params}`);
    return await response.json();
  },

  async networkingTogglePostFeatured(postId, isFeatured) {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/posts/${postId}/featured?is_featured=${isFeatured}`, { method: 'PUT' });
    return await response.json();
  },

  async networkingTogglePostPinned(postId, isPinned) {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/posts/${postId}/pinned?is_pinned=${isPinned}`, { method: 'PUT' });
    return await response.json();
  },

  async networkingDeletePost(postId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/posts/${postId}`, { method: 'DELETE' });
    return await response.json();
  },

  async networkingGetGroups(privacy = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (privacy) params.append('privacy', privacy);
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/groups?${params}`);
    return await response.json();
  },

  async networkingToggleGroupActive(groupId, isActive) {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/groups/${groupId}/active?is_active=${isActive}`, { method: 'PUT' });
    return await response.json();
  },

  async networkingGetLeads(status = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status) params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/leads?${params}`);
    return await response.json();
  },

  async networkingGetReferrals(status = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status) params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/referrals?${params}`);
    return await response.json();
  },

  async networkingGetPendingReferrals() {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/referrals/pending`);
    return await response.json();
  },

  async networkingVerifyReferral(referralId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/referrals/${referralId}/verify`, { method: 'POST' });
    return await response.json();
  },

  async networkingRejectReferral(referralId, reason = '') {
    const params = new URLSearchParams({ reason });
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/referrals/${referralId}/reject?${params}`, { method: 'POST' });
    return await response.json();
  },

  async networkingGetWallets(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/wallets?limit=${limit}`);
    return await response.json();
  },

  async networkingGetReferralCodes(isActive = true, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (isActive !== null) params.append('is_active', isActive);
    const response = await fetch(`${API_BASE}/api/v1/admin/networking/referral-codes?${params}`);
    return await response.json();
  },

  // ============ EMAIL (Phase 5) ============
  async emailGetDashboard() {
    const response = await fetch(`${API_BASE}/api/v1/admin/email/dashboard`);
    return await response.json();
  },

  async emailGetTemplates(category = null, isActive = null) {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (isActive !== null) params.append('is_active', isActive);
    const response = await fetch(`${API_BASE}/api/v1/admin/email/templates?${params}`);
    return await response.json();
  },

  async emailGetTemplateDetail(templateId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/email/templates/${templateId}`);
    return await response.json();
  },

  async emailToggleTemplate(templateId, isActive) {
    const response = await fetch(`${API_BASE}/api/v1/admin/email/templates/${templateId}/toggle?is_active=${isActive}`, { method: 'PUT' });
    return await response.json();
  },

  async emailGetVariables() {
    const response = await fetch(`${API_BASE}/api/v1/admin/email/variables`);
    return await response.json();
  },

  async emailGetLogs(status = null, templateId = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status) params.append('status', status);
    if (templateId) params.append('template_id', templateId);
    const response = await fetch(`${API_BASE}/api/v1/admin/email/logs?${params}`);
    return await response.json();
  },

  async emailSendTest(templateId, recipientEmail, testVariables = {}) {
    const params = new URLSearchParams({ template_id: templateId, recipient_email: recipientEmail });
    const response = await fetch(`${API_BASE}/api/v1/admin/email/test?${params}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testVariables)
    });
    return await response.json();
  },

  async emailGetConfig() {
    const response = await fetch(`${API_BASE}/api/v1/admin/email/config`);
    return await response.json();
  },

  // ============ MARKETING (Phase 5) ============
  async marketingGetDashboard() {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/dashboard`);
    return await response.json();
  },

  async marketingGetCampaigns(status = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status && status !== 'all') params.append('status', status);
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/campaigns?${params}`);
    return await response.json();
  },

  async marketingGetPosts(status = null, platform = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status && status !== 'all') params.append('status', status);
    if (platform && platform !== 'all') params.append('platform', platform);
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/posts?${params}`);
    return await response.json();
  },

  async marketingGetScheduledPosts(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/posts/scheduled?limit=${limit}`);
    return await response.json();
  },

  async marketingCreatePost(postData) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/posts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(postData)
    });
    return await response.json();
  },

  async marketingSchedulePost(postId, scheduledAt) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/posts/${postId}/schedule?scheduled_at=${scheduledAt}`, { method: 'PUT' });
    return await response.json();
  },

  async marketingPublishPost(postId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/posts/${postId}/publish`, { method: 'POST' });
    return await response.json();
  },

  async marketingDeletePost(postId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/posts/${postId}`, { method: 'DELETE' });
    return await response.json();
  },

  async marketingGenerateContent(params) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return await response.json();
  },

  async marketingGetSegments(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/segments?limit=${limit}`);
    return await response.json();
  },

  async marketingGetAutomations(isActive = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (isActive !== null) params.append('is_active', isActive);
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/automations?${params}`);
    return await response.json();
  },

  async marketingToggleAutomation(automationId, isActive) {
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/automations/${automationId}/toggle?is_active=${isActive}`, { method: 'PUT' });
    return await response.json();
  },

  async marketingGetHistory(platform = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (platform) params.append('platform', platform);
    const response = await fetch(`${API_BASE}/api/v1/admin/marketing/history?${params}`);
    return await response.json();
  },

  // ============ PARTNERS (Phase 6) ============
  async partnersGetDashboard() {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/dashboard`);
    return await response.json();
  },

  async partnersGetTypes() {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/types`);
    return await response.json();
  },

  async partnersGetRequests(status = null, partnerType = null, search = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (status) params.append('status', status);
    if (partnerType) params.append('partner_type', partnerType);
    if (search) params.append('search', search);
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/requests?${params}`);
    return await response.json();
  },

  async partnersGetRequestDetail(requestId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/requests/${requestId}`);
    return await response.json();
  },

  async partnersUpdateRequestStatus(requestId, status, adminNotes = null) {
    const params = new URLSearchParams({ status });
    if (adminNotes) params.append('admin_notes', adminNotes);
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/requests/${requestId}/status?${params}`, { method: 'PUT' });
    return await response.json();
  },

  async partnersConvertRequest(requestId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/requests/${requestId}/convert`, { method: 'POST' });
    return await response.json();
  },

  async partnersGetList(partnerType = null, isActive = null, search = null, limit = 50) {
    const params = new URLSearchParams({ limit });
    if (partnerType) params.append('partner_type', partnerType);
    if (isActive !== null) params.append('is_active', isActive);
    if (search) params.append('search', search);
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/list?${params}`);
    return await response.json();
  },

  async partnersGetDetail(partnerId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/${partnerId}`);
    return await response.json();
  },

  async partnersUpdate(partnerId, updates) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/${partnerId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    return await response.json();
  },

  async partnersToggleStatus(partnerId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/${partnerId}/toggle`, { method: 'PUT' });
    return await response.json();
  },

  async partnersVerify(partnerId, verified) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/${partnerId}/verify?verified=${verified}`, { method: 'PUT' });
    return await response.json();
  },

  async partnersUpdateCommission(partnerId, rate) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/${partnerId}/commission?rate=${rate}`, { method: 'PUT' });
    return await response.json();
  },

  async partnersGetEmailSettings() {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/email/settings`);
    return await response.json();
  },

  async partnersToggleEmailSetting(settingType) {
    const response = await fetch(`${API_BASE}/api/v1/admin/partners/email/toggle/${settingType}`, { method: 'PUT' });
    return await response.json();
  },

  // ============ BRANDING (Phase 6) ============
  async brandingGetDashboard() {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/dashboard`);
    return await response.json();
  },

  async brandingGetConfig() {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/config`);
    return await response.json();
  },

  async brandingGetLogos() {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/logos`);
    return await response.json();
  },

  async brandingGetLogoDetail(logoId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/logos/${logoId}`);
    return await response.json();
  },

  async brandingAddLogo(filename, url, language, logoType, fileSize = 0) {
    const params = new URLSearchParams({ filename, url, language, logo_type: logoType, file_size: fileSize });
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/logos?${params}`, { method: 'POST' });
    return await response.json();
  },

  async brandingDeleteLogo(logoId) {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/logos/${logoId}`, { method: 'DELETE' });
    return await response.json();
  },

  async brandingGetColors() {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/colors`);
    return await response.json();
  },

  async brandingUpdateColor(colorKey, hexValue, name = null) {
    const params = new URLSearchParams({ hex_value: hexValue });
    if (name) params.append('name', name);
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/colors/${colorKey}?${params}`, { method: 'PUT' });
    return await response.json();
  },

  async brandingResetColors() {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/colors/reset`, { method: 'POST' });
    return await response.json();
  },

  async brandingGetDocumentTypes() {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/document-types`);
    return await response.json();
  },

  async brandingLogDocumentGeneration(templateType, language, title = null, recipient = null) {
    const params = new URLSearchParams({ template_type: templateType, language });
    if (title) params.append('title', title);
    if (recipient) params.append('recipient', recipient);
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/documents/log?${params}`, { method: 'POST' });
    return await response.json();
  },

  async brandingGetDocumentHistory(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/documents/history?limit=${limit}`);
    return await response.json();
  },

  async brandingGetUploadHistory(limit = 50) {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/uploads/history?limit=${limit}`);
    return await response.json();
  },

  async brandingGetAssets() {
    const response = await fetch(`${API_BASE}/api/v1/admin/branding/assets`);
    return await response.json();
  }
};

export default AdminService;
