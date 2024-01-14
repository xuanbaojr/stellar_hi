"use client"

import { ChatbotUIContext } from "@/context/context"
import { getProfileByUserId, updateProfile } from "@/db/profile"
import { uploadImage } from "@/db/storage/profile-images"
import { getWorkspacesByUserId, updateWorkspace } from "@/db/workspaces"
import { supabase } from "@/lib/supabase/browser-client"
import { TablesUpdate } from "@/supabase/types"
import { ChatSettings } from "@/types"
import { useRouter } from "next/navigation"
import { useContext, useEffect, useState } from "react"
import { FinishStep } from "../../components/setup/finish-step"
import { ProfileStep } from "../../components/setup/profile-step"
import {
  SETUP_STEP_COUNT,
  StepContainer
} from "../../components/setup/step-container"
import { WorkspaceStep } from "../../components/setup/workspace-step"

export default function SetupPage() {
  const { profile, setProfile, setSelectedWorkspace, setWorkspaces } =
    useContext(ChatbotUIContext)

  const router = useRouter()

  const [loading, setLoading] = useState(true)

  const [currentStep, setCurrentStep] = useState(1)

  // Profile Step
  const [profileContext, setProfileContext] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [username, setUsername] = useState(profile?.username || "")
  const [usernameAvailable, setUsernameAvailable] = useState(true)
  const [profileImageSrc, setProfileImageSrc] = useState("")
  const [profileImage, setProfileImage] = useState<File | null>(null)

  // Workspace Step
  const [workspaceInstructions, setWorkspaceInstructions] = useState("")
  const [defaultChatSettings, setDefaultChatSettings] = useState<ChatSettings>({
    model: "gpt-35-turbo",
    prompt: "You are a friendly, helpful AI assistant.",
    temperature: 0.5,
    contextLength: 4096,
    includeProfileContext: true,
    includeWorkspaceInstructions: true,
    embeddingsProvider: "openai"
  })

  const handleShouldProceed = (proceed: boolean) => {
    if (proceed) {
      if (currentStep === SETUP_STEP_COUNT) {
        handleSaveSetupSetting()
      } else {
        setCurrentStep(currentStep + 1)
      }
    } else {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSaveSetupSetting = async () => {
    if (!profile) return

    let profileImageUrl = ""
    let profileImagePath = ""

    if (profileImage) {
      const { path, url } = await uploadImage(profile, profileImage)
      profileImageUrl = url
      profileImagePath = path
    }

    const updateProfilePayload: TablesUpdate<"profiles"> = {
      ...profile,
      has_onboarded: true,
      display_name: displayName,
      username,
      profile_context: profileContext,
      image_url: profileImageUrl,
      image_path: profileImageUrl
    }

    const updatedProfile = await updateProfile(profile.id, updateProfilePayload)

    setProfile(updatedProfile)

    const updateHomeWorkspacePayload: TablesUpdate<"workspaces"> = {
      default_context_length: defaultChatSettings.contextLength,
      default_model: defaultChatSettings.model,
      default_prompt: defaultChatSettings.prompt,
      default_temperature: defaultChatSettings.temperature,
      include_profile_context: defaultChatSettings.includeProfileContext,
      include_workspace_instructions:
        defaultChatSettings.includeWorkspaceInstructions,
      instructions: workspaceInstructions,
      embeddings_provider: defaultChatSettings.embeddingsProvider
    }

    const workspaces = await getWorkspacesByUserId(profile.user_id)
    const homeWorkspace = workspaces.find(w => w.is_home)

    // There will always be a home workspace
    const updatedWorkspace = await updateWorkspace(
      homeWorkspace!.id,
      updateHomeWorkspacePayload
    )

    setSelectedWorkspace(updatedWorkspace)
    setWorkspaces(
      workspaces.map(workspace =>
        workspace.id === updatedWorkspace.id ? updatedWorkspace : workspace
      )
    )

    router.push("/chat")
  }

  const renderStep = (stepNum: number) => {
    switch (stepNum) {
      // Profile Step
      case 1:
        return (
          <StepContainer
            stepDescription="Let's create your profile."
            stepNum={currentStep}
            stepTitle="Welcome to Chatbot Stellar"
            onShouldProceed={handleShouldProceed}
            showNextButton={!!(displayName && username && usernameAvailable)}
            showBackButton={false}
          >
            <ProfileStep
              profileContext={profileContext}
              profileImageSrc={profileImageSrc}
              profileImage={profileImage}
              username={username}
              usernameAvailable={usernameAvailable}
              displayName={displayName}
              onProfileContextChange={setProfileContext}
              onProfileImageChangeSrc={setProfileImageSrc}
              onProfileImageChange={setProfileImage}
              onUsernameAvailableChange={setUsernameAvailable}
              onUsernameChange={setUsername}
              onDisplayNameChange={setDisplayName}
            />
          </StepContainer>
        )

      // Workspace Step
      case 2:
        return (
          <StepContainer
            stepDescription="Select the default settings for your home workspace."
            stepNum={currentStep}
            stepTitle="Create Workspace"
            onShouldProceed={handleShouldProceed}
            showNextButton={true}
            showBackButton={true}
          >
            <WorkspaceStep
              chatSettings={defaultChatSettings}
              workspaceInstructions={workspaceInstructions}
              onChatSettingsChange={setDefaultChatSettings}
              onWorkspaceInstructionsChange={setWorkspaceInstructions}
            />
          </StepContainer>
        )

      // Finish Step
      case 3:
        return (
          <StepContainer
            stepDescription="You are all set up!"
            stepNum={currentStep}
            stepTitle="Setup Complete"
            onShouldProceed={handleShouldProceed}
            showNextButton={true}
            showBackButton={true}
          >
            <FinishStep displayName={displayName} />
          </StepContainer>
        )
      default:
        return null
    }
  }

  useEffect(() => {
    ;(async () => {
      const session = (await supabase.auth.getSession()).data.session

      if (!session) {
        router.push("/login")
      } else {
        const user = session.user

        const profile = await getProfileByUserId(user.id)
        setProfile(profile)

        if (!profile.has_onboarded) {
          setLoading(false)
        } else {
          router.push("/chat")
        }
      }
    })()
  }, [])

  if (loading) {
    return null
  }

  return (
    <div className="flex h-full items-center justify-center">
      {renderStep(currentStep)}
    </div>
  )
}
